# app/routes/__init__.py
from fastapi import APIRouter
from app.routes import dashboard
from app.routes import driver_stats
from app.routes import live
from app.routes import privacy

router = APIRouter()

# Include the dashboard routes (tagged for clarity)
router.include_router(dashboard.router, tags=["dashboard"])
router.include_router(driver_stats.router, tags=["driver_stats"])
# router.include_router(live.router, tags=["live"])
router.include_router(privacy.router, tags=["privacy"])
