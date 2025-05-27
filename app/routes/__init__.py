# app/routes/__init__.py
from app.routes import driver_stats
from app.routes import live
from fastapi import APIRouter
from app.routes import dashboard  # Import additional route modules as needed

router = APIRouter()

# Include the dashboard routes (tagged for clarity)
router.include_router(dashboard.router, tags=["dashboard"])
router.include_router(driver_stats.router, tags=["driver_stats"])
# router.include_router(live.router, tags=["live"])