from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.cache import get_cached_data
from .ubpk_metrics import (
    _parse_week,
    _week_string,
    _weekly_driver_map,
    placeholder_history,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _driver_history(driver_id: str) -> List[Dict]:
    payload = get_cached_data()
    if not payload:
        return placeholder_history(driver_id)
    rows = payload.get("dashboard_trip_metrics", [])
    history: Dict[str, List[float]] = {}
    for row in rows:
        if row.get("driverProfileId") != driver_id:
            continue
        start = row.get("start_time")
        wk = None
        if start:
            try:
                iso_year, iso_week, _ = date.fromisoformat(start).isocalendar()
                wk = _week_string(iso_year, iso_week)
            except Exception:
                wk = None
        if not wk:
            continue
        history.setdefault(wk, []).append(row.get("invalidSensorDataCount", 0) / max(1, row.get("totalSensorDataCount", 1)))

    if not history:
        return placeholder_history(driver_id)
    return [
        {"week": week, "ubpk": sum(vals) / len(vals)} for week, vals in sorted(history.items())
    ]


@router.get("/driver/{driver_id}", response_class=HTMLResponse)
async def driver_analysis_home(request: Request, driver_id: str):
    weeks = [h["week"] for h in _driver_history(driver_id)]
    return templates.TemplateResponse(
        "pages/driver_analysis.html",
        {"request": request, "driver_id": driver_id, "weeks": weeks},
    )


@router.get("/driver/{driver_id}/trend", response_class=HTMLResponse)
async def driver_trend(request: Request, driver_id: str, week: Optional[str] = None):
    if week is None:
        today = date.today()
        week = _week_string(*today.isocalendar()[:2])
    try:
        year, wk = _parse_week(week)
    except ValueError:
        raise HTTPException(400, "Invalid week format")
    driver_map = _weekly_driver_map(year, wk)
    value = None
    vals = driver_map.get(driver_id)
    if vals:
        value = sum(vals) / len(vals)
    history = _driver_history(driver_id)
    context = {
        "request": request,
        "driver_id": driver_id,
        "week": week,
        "ubpk": value,
        "history": history,
    }
    if "application/json" in request.headers.get("accept", ""):
        return context
    return templates.TemplateResponse("pages/driver_trend.html", context)


@router.get("/driver/{driver_id}/history", response_class=HTMLResponse)
async def driver_history_page(request: Request, driver_id: str):
    history = _driver_history(driver_id)
    return templates.TemplateResponse(
        "pages/driver_history.html",
        {"request": request, "driver_id": driver_id, "history": history},
    )
