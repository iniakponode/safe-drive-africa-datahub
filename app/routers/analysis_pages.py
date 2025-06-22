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
    _driver_history,
    driver_week_metrics,
    driver_history_metrics,
    trip_metrics,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/driver/{driver_id}", response_class=HTMLResponse)
async def driver_analysis_home(request: Request, driver_id: str):
    # Current week metrics for initial display
    today = date.today()
    year, wk = today.isocalendar()[:2]
    driver_map = _weekly_driver_map(year, wk)
    vals = driver_map.get(driver_id)
    current_metrics = None
    if vals:
        current_metrics = {
            "week": _week_string(year, wk),
            "ubpk": sum(vals) / len(vals),
            "numTrips": len(vals),
        }

    return templates.TemplateResponse(
        "pages/driver_analysis.html",
        {"request": request, "driver_id": driver_id, "current": current_metrics},
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


@router.get("/trip/{trip_id}", response_class=HTMLResponse)
async def trip_analysis_page(request: Request, trip_id: str):
    try:
        metrics = trip_metrics(trip_id)
    except HTTPException as exc:
        if exc.status_code == 404:
            metrics = None
        else:
            raise
    return templates.TemplateResponse(
        "pages/trip_analysis.html",
        {"request": request, "trip_id": trip_id, "metrics": metrics},
    )
