from fastapi import APIRouter
from datetime import datetime, timedelta
from statistics import mean, NormalDist
from math import sqrt
from typing import List, Optional

from app.cache import get_cached_data

router = APIRouter(prefix="/api/behaviour_metrics", tags=["behaviour_metrics"])


def _compute_trip_stats():
    data = get_cached_data() or {}
    trip_metrics = data.get("dashboard_trip_metrics", [])
    processed = []
    for row in trip_metrics:
        total = row.get("totalSensorDataCount", 0)
        invalid = row.get("invalidSensorDataCount", 0)
        driver_id = row.get("driverProfileId")
        trip_id = row.get("tripId")
        ubpk = invalid / total if total else 0
        processed.append({
            "trip_id": trip_id,
            "driverProfileId": driver_id,
            "ubpk": ubpk,
            "invalid": invalid,
            "total": total,
        })
    return processed


def _aggregate_per_driver(trip_stats):
    aggregates = {}
    for row in trip_stats:
        driver_id = row.get("driverProfileId")
        if not driver_id:
            continue
        agg = aggregates.setdefault(driver_id, {"invalid": 0, "total": 0})
        agg["invalid"] += row["invalid"]
        agg["total"] += row["total"]
    result = []
    for driver_id, vals in aggregates.items():
        total = vals["total"]
        invalid = vals["invalid"]
        ubpk = invalid / total if total else 0
        result.append({"driverProfileId": driver_id, "ubpk": ubpk})
    return result


def _weekly_metrics(trip_stats, week_start: Optional[str] = None):
    if week_start is None:
        week_start = (
            datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        ).date().isoformat()
    per_driver = {}
    for row in trip_stats:
        driver_id = row.get("driverProfileId")
        if not driver_id:
            continue
        agg = per_driver.setdefault(driver_id, {"invalid": 0, "total": 0})
        agg["invalid"] += row["invalid"]
        agg["total"] += row["total"]
    results = []
    for driver_id, vals in per_driver.items():
        total = vals["total"]
        invalid = vals["invalid"]
        ubpk = invalid / total if total else 0
        results.append({"driverProfileId": driver_id, "week_start": week_start, "ubpk": ubpk})
    return results


def _weekly_history(trip_stats: List[dict], num_weeks: int = 4):
    """Return UBPK values for a sequence of weeks.

    Because the cached data lacks explicit timestamps, this simply repeats the
    current week's UBPK for the requested number of weeks so that the UI can
    display a trend placeholder.
    """
    history = []
    current_week_start = (
        datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    ).date()
    base = _weekly_metrics(trip_stats, current_week_start.isoformat())
    value = base[0]["ubpk"] if base else 0
    driver_id = base[0].get("driverProfileId") if base else None
    for i in range(num_weeks):
        week_start = (current_week_start - timedelta(weeks=num_weeks - i - 1)).isoformat()
        history.append({
            "driverProfileId": driver_id,
            "week_start": week_start,
            "ubpk": value,
        })
    return history


def _two_sample_t_test(a, b):
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


def _improvement_analysis(trip_stats):
    by_driver = {}
    for row in trip_stats:
        driver_id = row.get("driverProfileId")
        if not driver_id:
            continue
        by_driver.setdefault(driver_id, []).append(row["ubpk"])

    results = []
    for driver_id, vals in by_driver.items():
        if len(vals) < 2:
            results.append({"driverProfileId": driver_id, "improved": False, "p_value": 1.0})
            continue
        mid = len(vals) // 2
        first, second = vals[:mid], vals[mid:]
        t_stat, p_val = _two_sample_t_test(first, second)
        improved = mean(second) < mean(first) and p_val < 0.05
        results.append({"driverProfileId": driver_id, "improved": improved, "p_value": p_val})
    return results


@router.get("/ubpk")
async def ubpk_per_driver():
    trip_stats = _compute_trip_stats()
    return _aggregate_per_driver(trip_stats)


@router.get("/trip")
async def ubpk_per_trip():
    return _compute_trip_stats()


@router.get("/weekly")
async def weekly_metrics(week: Optional[str] = None):
    trip_stats = _compute_trip_stats()
    return _weekly_metrics(trip_stats, week)


@router.get("/history")
async def weekly_history(weeks: int = 4):
    trip_stats = _compute_trip_stats()
    return _weekly_history(trip_stats, weeks)


@router.get("/improvement")
async def improvement():
    trip_stats = _compute_trip_stats()
    return _improvement_analysis(trip_stats)
