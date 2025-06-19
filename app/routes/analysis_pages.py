from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routes.behaviour_metrics import (
    _compute_trip_stats,
    _aggregate_per_driver,
    _weekly_metrics,
    _improvement_analysis,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/analysis/driver/{driver_id}", response_class=HTMLResponse)
async def driver_analysis_page(driver_id: str, request: Request):
    trip_stats = [row for row in _compute_trip_stats() if row.get("driverProfileId") == driver_id]
    if not trip_stats:
        return templates.TemplateResponse(
            "pages/driver_analysis.html",
            {"request": request, "driver_id": driver_id, "not_found": True},
        )
    overall = _aggregate_per_driver(trip_stats)[0]
    weekly = _weekly_metrics(trip_stats)
    improvement = _improvement_analysis(trip_stats)[0]
    return templates.TemplateResponse(
        "pages/driver_analysis.html",
        {
            "request": request,
            "driver_id": driver_id,
            "overall": overall,
            "trips": trip_stats,
            "weekly": weekly,
            "improvement": improvement,
        },
    )


@router.get("/analysis/trip/{trip_id}", response_class=HTMLResponse)
async def trip_analysis_page(trip_id: str, request: Request):
    trip_stat = next((row for row in _compute_trip_stats() if row.get("trip_id") == trip_id), None)
    return templates.TemplateResponse(
        "pages/trip_analysis.html",
        {"request": request, "trip": trip_stat, "trip_id": trip_id},
    )
