from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.cache import get_cached_data
from app.services.data_service import fetch_all_data, process_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    cached = get_cached_data()
    if cached is None or "aggregates" not in cached: # Ensure aggregates key exists
        data = await fetch_all_data()
        aggregates = process_data(data)
        # Optionally, you might want to update the cache here if it was None
        # This depends on how your cache is populated initially if empty
    else:
        aggregates = cached.get("aggregates")

    # Add Cache-Control headers
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",  # For HTTP/1.0 compatibility
        "Expires": "0"  # For proxy servers
    }
    return templates.TemplateResponse(
        "pages/index.html",
        {"request": request, "aggregates": aggregates},
        headers=headers
    )