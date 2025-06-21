from typing import Optional
from fastapi import APIRouter

from app.services.behaviour_metrics import (
    compute_trip_stats,
    aggregate_per_driver,
    weekly_metrics,
    weekly_history,
    improvement_analysis,
)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/trip")
async def trip_metrics():
    return await compute_trip_stats()


@router.get("/driver")
async def driver_metrics():
    trip_stats = await compute_trip_stats()
    return aggregate_per_driver(trip_stats)


@router.get("/weekly")
async def weekly_metrics_endpoint(week: Optional[str] = None):
    trip_stats = await compute_trip_stats()
    return weekly_metrics(trip_stats, week)


@router.get("/history")
async def weekly_history_endpoint(weeks: int = 4):
    trip_stats = await compute_trip_stats()
    return weekly_history(trip_stats, weeks)


@router.get("/improvement")
async def improvement_endpoint():
    trip_stats = await compute_trip_stats()
    return improvement_analysis(trip_stats)
