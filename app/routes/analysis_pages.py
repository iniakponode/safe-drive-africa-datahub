from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.behaviour_metrics import (
    compute_trip_stats,
    aggregate_per_driver,
    weekly_metrics,
    weekly_history,
    improvement_analysis,
)
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/analysis/driver/{driver_id}", response_class=HTMLResponse)
async def driver_analysis_page(driver_id: str, request: Request, week: Optional[str] = None):
    all_stats = await compute_trip_stats()
    trip_stats = [row for row in all_stats if row.get("driverProfileId") == driver_id]
    if not trip_stats:
        return templates.TemplateResponse(
            "pages/driver_analysis.html",
            {"request": request, "driver_id": driver_id, "not_found": True},
        )
    overall = aggregate_per_driver(trip_stats)[0]
    weekly = weekly_metrics(trip_stats, week)
    improvement = improvement_analysis(trip_stats)[0]
    return templates.TemplateResponse(
        "pages/driver_analysis.html",
        {
            "request": request,
            "driver_id": driver_id,
            "overall": overall,
            "trips": trip_stats,
            "weekly": weekly,
            "week": week or (weekly[0]["week_start"] if weekly else ""),
            "improvement": improvement,
        },
    )


@router.get("/analysis/driver/{driver_id}/history", response_class=HTMLResponse)
async def driver_history_page(driver_id: str, request: Request):
    all_stats = await compute_trip_stats()
    trip_stats = [row for row in all_stats if row.get("driverProfileId") == driver_id]
    if not trip_stats:
        return templates.TemplateResponse(
            "pages/driver_history.html",
            {"request": request, "driver_id": driver_id, "not_found": True},
        )
    history = weekly_history(trip_stats)
    return templates.TemplateResponse(
        "pages/driver_history.html",
        {"request": request, "driver_id": driver_id, "history": history},
    )


@router.get("/analysis/trip/{trip_id}", response_class=HTMLResponse)
async def trip_analysis_page(trip_id: str, request: Request):
    all_stats = await compute_trip_stats()
    trip_stat = next((row for row in all_stats if row.get("trip_id") == trip_id), None)
    return templates.TemplateResponse(
        "pages/trip_analysis.html",
        {"request": request, "trip": trip_stat, "trip_id": trip_id},
    )
