# app/routes/__init__.py
from fastapi import APIRouter
from routes import dashboard  # Import additional route modules as needed

router = APIRouter()

# Include the dashboard routes (tagged for clarity)
router.include_router(dashboard.router, tags=["dashboard"])