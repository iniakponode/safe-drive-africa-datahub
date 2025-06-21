from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import get_cached_data

router = APIRouter()


def _parse_week(week: str) -> tuple[int, int]:
    try:
        year_str, week_str = week.split("-W")
        return int(year_str), int(week_str)
    except Exception as exc:  # pragma: no cover - invalid user input
        raise ValueError("Invalid week format, expected YYYY-WW") from exc


def _week_string(year: int, week: int) -> str:
    return f"{year}-W{week:02d}"


def _week_from_date(date_str: str) -> Optional[tuple[int, int]]:
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:  # pragma: no cover - parse failure
        return None
    iso_year, iso_week, _ = dt.isocalendar()
    return iso_year, iso_week


def _compute_trip_ubpk(row: Dict) -> Optional[float]:
    total = row.get("totalSensorDataCount") or 0
    invalid = row.get("invalidSensorDataCount") or 0
    if total <= 0:
        return None
    return invalid / total


def _gather_trip_rows() -> List[Dict]:
    payload = get_cached_data()
    if not payload:
        raise HTTPException(status_code=404, detail="No cached data available")
    return payload.get("dashboard_trip_metrics", [])


@router.get("/trip")
async def per_trip_metrics() -> List[Dict]:
    """Return UBPK metrics for each trip."""
    rows = _gather_trip_rows()
    metrics: List[Dict] = []
    for row in rows:
        ubpk = _compute_trip_ubpk(row)
        metrics.append({
            "tripId": row.get("tripId"),
            "driverProfileId": row.get("driverProfileId"),
            "start_time": row.get("start_time"),
            "invalidSensorDataCount": row.get("invalidSensorDataCount", 0),
            "totalSensorDataCount": row.get("totalSensorDataCount", 0),
            "ubpk": ubpk,
        })
    return metrics


def _weekly_driver_map(year: int, week: int) -> Dict[str, List[float]]:
    data = _gather_trip_rows()
    mapping: Dict[str, List[float]] = {}
    for row in data:
        st = row.get("start_time")
        wk = _week_from_date(st) if st else None
        if wk != (year, week):
            continue
        ubpk = _compute_trip_ubpk(row)
        if ubpk is None:
            continue
        mapping.setdefault(row.get("driverProfileId"), []).append(ubpk)
    return mapping


@router.get("/weekly")
async def weekly_metrics(week: Optional[str] = Query(None)) -> List[Dict]:
    today = date.today()
    year, wk = today.isocalendar()[:2] if week is None else _parse_week(week)

    driver_map = _weekly_driver_map(year, wk)
    if not driver_map:
        raise HTTPException(400, "No trip data for that week")

    results = []
    for driver_id, values in driver_map.items():
        results.append({
            "driverProfileId": driver_id,
            "week": _week_string(year, wk),
            "ubpk": sum(values) / len(values),
            "numTrips": len(values),
        })
    return results


def _paired_t_test(current: List[float], previous: List[float]) -> tuple[float, float]:
    if len(current) != len(previous) or len(current) < 2:
        raise ValueError("Insufficient paired samples")
    diffs = [c - p for c, p in zip(current, previous)]
    n = len(diffs)
    mean_diff = sum(diffs) / n
    var = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    import math
    t_stat = mean_diff / math.sqrt(var / n)
    # Normal approximation of two-sided p-value
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))
    return p, mean_diff


@router.get("/improvement")
async def improvement_analysis(week: Optional[str] = Query(None)) -> Dict:
    today = date.today()
    year, wk = today.isocalendar()[:2] if week is None else _parse_week(week)
    prev_dt = date.fromisocalendar(year, wk, 1) - timedelta(weeks=1)
    prev_year, prev_week = prev_dt.isocalendar()[:2]

    current_map = _weekly_driver_map(year, wk)
    prev_map = _weekly_driver_map(prev_year, prev_week)

    drivers = sorted(set(current_map) & set(prev_map))
    if len(drivers) < 2:
        raise HTTPException(400, "Not enough driver data for paired t-test")

    current_values = [sum(current_map[d]) / len(current_map[d]) for d in drivers]
    prev_values = [sum(prev_map[d]) / len(prev_map[d]) for d in drivers]
    p_value, mean_diff = _paired_t_test(current_values, prev_values)

    return {
        "week": _week_string(year, wk),
        "previous_week": _week_string(prev_year, prev_week),
        "p_value": p_value,
        "mean_difference": mean_diff,
    }


def placeholder_history(driver_id: str, weeks: int = 8) -> List[Dict]:
    today = date.today()
    history: List[Dict] = []
    for i in range(weeks):
        dt = today - timedelta(weeks=i)
        year, wk, _ = dt.isocalendar()
        history.append({
            "week": _week_string(year, wk),
            "ubpk": 0.0,
        })
    history.reverse()
    return history
