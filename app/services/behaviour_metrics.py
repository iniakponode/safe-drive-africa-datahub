from __future__ import annotations
from datetime import datetime, timedelta
from statistics import mean, NormalDist
from math import sqrt
from typing import List, Dict, Optional, Tuple
import asyncio
import httpx

from app.services.data_service import (
    fetch_and_validate_data,
    DriverProfileModel,
    TripModel,
    SensorDataModel,
    DRIVERS_URL,
    TRIPS_URL,
    SENSOR_URL,
)


async def _fetch_live_data() -> Tuple[List[DriverProfileModel], List[TripModel], List[SensorDataModel]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        drivers_task = fetch_and_validate_data(client, DRIVERS_URL, DriverProfileModel, is_profile_api=True)
        trips_task = fetch_and_validate_data(client, TRIPS_URL, TripModel, paged=True, chunk_size=5000)
        sensors_task = fetch_and_validate_data(client, SENSOR_URL, SensorDataModel, paged=True, chunk_size=10000)
        drivers, trips, sensors = await asyncio.gather(drivers_task, trips_task, sensors_task)
    return drivers, trips, sensors


def _detect_events(values: List[float]) -> Tuple[int, int, int, float]:
    harsh = rapid = speeding = 0
    distance_m = 0.0
    prev: Optional[float] = None
    for v in values:
        speed = float(v)
        distance_m += speed
        if speed * 3.6 > 100:
            speeding += 1
        if prev is not None:
            delta = speed - prev
            if delta <= -4:
                harsh += 1
            if delta >= 4:
                rapid += 1
        prev = speed
    return harsh, rapid, speeding, distance_m / 1000.0


def _compute_trip_stats_from_data(trips: List[TripModel], sensors: List[SensorDataModel]) -> List[Dict[str, float]]:
    sensors_by_trip: Dict[str, List[float]] = {}
    for s in sensors:
        if not s.trip_id:
            continue
        sensors_by_trip.setdefault(s.trip_id, []).extend(s.values)

    processed = []
    for trip in trips:
        values = sensors_by_trip.get(trip.trip_id, [])
        if not values:
            continue
        hb, ra, sp, dist_km = _detect_events(values)
        total_events = hb + ra + sp
        ubpk = total_events / dist_km if dist_km else 0.0
        processed.append(
            {
                "trip_id": trip.trip_id,
                "driverProfileId": trip.driverProfileId,
                "startTime": trip.startTime,
                "distance_km": dist_km,
                "total_events": total_events,
                "ubpk": ubpk,
            }
        )
    return processed


async def compute_trip_stats() -> List[Dict[str, float]]:
    _drivers, trips, sensors = await _fetch_live_data()
    return _compute_trip_stats_from_data(trips, sensors)


def aggregate_per_driver(trip_stats: List[Dict[str, float]]) -> List[Dict[str, float]]:
    aggregates: Dict[str, Dict[str, float]] = {}
    for row in trip_stats:
        driver = row.get("driverProfileId")
        if not driver:
            continue
        agg = aggregates.setdefault(driver, {"events": 0.0, "distance": 0.0})
        agg["events"] += row["total_events"]
        agg["distance"] += row["distance_km"]
    results = []
    for driver, vals in aggregates.items():
        ubpk = vals["events"] / vals["distance"] if vals["distance"] else 0.0
        results.append({"driverProfileId": driver, "ubpk": ubpk})
    return results


def weekly_metrics(trip_stats: List[Dict[str, float]], week_start: Optional[str] = None) -> List[Dict[str, float]]:
    if week_start is None:
        week_start_dt = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    else:
        try:
            week_start_dt = datetime.fromisoformat(week_start)
        except ValueError:
            week_start_dt = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_end_dt = week_start_dt + timedelta(days=7)
    per_driver: Dict[str, Dict[str, float]] = {}
    for row in trip_stats:
        st = row.get("startTime")
        if not st:
            continue
        try:
            start_dt = datetime.fromisoformat(st)
        except ValueError:
            continue
        if not (week_start_dt <= start_dt < week_end_dt):
            continue
        driver = row.get("driverProfileId")
        if not driver:
            continue
        agg = per_driver.setdefault(driver, {"events": 0.0, "distance": 0.0})
        agg["events"] += row["total_events"]
        agg["distance"] += row["distance_km"]
    results = []
    for driver, vals in per_driver.items():
        ubpk = vals["events"] / vals["distance"] if vals["distance"] else 0.0
        results.append({"driverProfileId": driver, "week_start": week_start_dt.date().isoformat(), "ubpk": ubpk})
    return results


def weekly_history(trip_stats: List[Dict[str, float]], num_weeks: int = 4) -> List[Dict[str, float]]:
    history = []
    base_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    for i in range(num_weeks):
        week_start_dt = base_start - timedelta(weeks=num_weeks - i - 1)
        metrics = weekly_metrics(trip_stats, week_start_dt.date().isoformat())
        value = metrics[0]["ubpk"] if metrics else 0.0
        driver_id = metrics[0].get("driverProfileId") if metrics else None
        history.append({"driverProfileId": driver_id, "week_start": week_start_dt.date().isoformat(), "ubpk": value})
    return history


def _two_sample_t_test(a: List[float], b: List[float]) -> Tuple[float, float]:
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return 0.0, 1.0
    m1, m2 = mean(a), mean(b)
    v1 = sum((x - m1) ** 2 for x in a) / (n1 - 1)
    v2 = sum((x - m2) ** 2 for x in b) / (n2 - 1)
    pooled = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
    if pooled == 0:
        return 0.0, 1.0
    t_stat = (m1 - m2) / sqrt(pooled * (1 / n1 + 1 / n2))
    p_value = (1 - NormalDist().cdf(abs(t_stat))) * 2
    return t_stat, p_value


def improvement_analysis(trip_stats: List[Dict[str, float]]) -> List[Dict[str, float]]:
    by_driver: Dict[str, List[Tuple[str, float]]] = {}
    for row in trip_stats:
        driver = row.get("driverProfileId")
        if not driver:
            continue
        by_driver.setdefault(driver, []).append((row.get("startTime"), row["ubpk"]))
    results = []
    for driver, vals in by_driver.items():
        vals.sort(key=lambda x: x[0] or "")
        ubpks = [v for _, v in vals]
        if len(ubpks) < 2:
            results.append({"driverProfileId": driver, "improved": False, "p_value": 1.0})
            continue
        mid = len(ubpks) // 2
        first, second = ubpks[:mid], ubpks[mid:]
        _, p_val = _two_sample_t_test(first, second)
        improved = mean(second) < mean(first) and p_val < 0.05
        results.append({"driverProfileId": driver, "improved": improved, "p_value": p_val})
    return results
