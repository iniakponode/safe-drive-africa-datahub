# app/routes/__init__.py
from fastapi import APIRouter
from app.routes import dashboard
from app.routes import driver_stats
from app.routes import live
from app.routes import privacy
from app.routes import metrics_api
from app.routes import analysis_pages

router = APIRouter()

# Include the dashboard routes (tagged for clarity)
router.include_router(dashboard.router, tags=["dashboard"])
router.include_router(driver_stats.router, tags=["driver_stats"])
# router.include_router(live.router, tags=["live"])
router.include_router(privacy.router, tags=["privacy"])
router.include_router(metrics_api.router)
router.include_router(analysis_pages.router)
