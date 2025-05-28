from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.cache import get_cached_data
# Import the new main fetching/processing function for the case where cache might be initially empty
from app.services.data_service import fetch_all_processed_data # This is the refactored function

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/drivers", response_class=HTMLResponse)
async def driver_statistics_page(request: Request):
    """
    Serves the driver statistics page.
    It retrieves processed data from a cache. If the cache is empty (e.g., on first startup),
    it can optionally perform an initial data fetch and process.
    """
    processed_data_payload = get_cached_data()
    data_unavailable_for_template = False

    # Define the default structure for view_stats to ensure the template always has expected variables
    view_stats = {
        "driver_list": [],
        "total_num_trips": 0,
        "total_valid_sensor_data": 0,
        "total_invalid_sensor_data": 0
    }

    if processed_data_payload is None:
        logger.info("Driver Stats Page: Cache is empty. Attempting to fetch and process data for this request.")
        # This behavior (fetching directly if cache is empty) makes the first request potentially slow.
        # Alternative: Set data_unavailable_for_template = True and rely on background cache refresh.
        try:
            processed_data_payload = await fetch_all_processed_data()
            if processed_data_payload is None: # If the fetch/process itself returned None
                logger.warning("Driver Stats Page: Initial data fetch/processing returned None.")
                data_unavailable_for_template = True
        except Exception as e:
            logger.error(f"Driver Stats Page: Critical error during initial data fetch on cache miss: {e}", exc_info=True)
            processed_data_payload = None # Ensure it's None if fetch fails
            data_unavailable_for_template = True

    if processed_data_payload:
        # Extract the 'driver_focused_stats' part from the overall payload
        retrieved_stats = processed_data_payload.get("driver_focused_stats")
        if retrieved_stats and isinstance(retrieved_stats, dict):
            view_stats = {
                "driver_list": retrieved_stats.get("driver_list", []),
                "total_num_trips": retrieved_stats.get("total_num_trips", 0),
                "total_valid_sensor_data": retrieved_stats.get("total_valid_sensor_data", 0),
                "total_invalid_sensor_data": retrieved_stats.get("total_invalid_sensor_data", 0)
            }
        else:
            logger.warning("Driver Stats Page: 'driver_focused_stats' key missing or not a dict in cached payload. Using default empty stats.")
            data_unavailable_for_template = True # Data structure issue
    else:
        # This case is hit if cache was None and the initial fetch also failed or was skipped.
        if not data_unavailable_for_template: # Avoid double logging if fetch failed and already set the flag
             logger.warning("Driver Stats Page: No data available from cache or initial fetch. Serving with empty/default stats.")
        data_unavailable_for_template = True

    # HTTP headers to prevent browser caching of this dynamic HTML page
    response_headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    # The template "pages/driver_stats.html" expects a context variable, likely named "stats".
    # This "stats" variable should contain a list of drivers (e.g., "driver_list")
    # and the various total counts.
    return templates.TemplateResponse(
        "pages/driver_stats.html",
        {
            "request": request,
            "stats": view_stats,  # Pass the prepared view_stats object
            "data_unavailable": data_unavailable_for_template # Optional flag for the template
        },
        headers=response_headers
    )