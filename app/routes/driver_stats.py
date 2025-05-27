from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.cache import get_cached_data
from app.services.data_service import fetch_all_data, process_driver_data # Ensure process_driver_data is imported

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/drivers", response_class=HTMLResponse)
async def driver_stats(request: Request):
    cached = get_cached_data()
    stats = None
    if cached is None or "driver_stats" not in cached: # Ensure driver_stats key exists
        data = await fetch_all_data()
        stats = process_driver_data(data)
        # Optionally, update cache
    else:
        stats = cached.get("driver_stats")

    # Add Cache-Control headers
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return templates.TemplateResponse(
        "pages/driver_stats.html",
        {"request": request, "stats": stats},
        headers=headers
    )