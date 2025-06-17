from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.cache import get_cached_data
from app.services.data_service import fetch_all_processed_data

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def main_dashboard_page(request: Request):
    processed_data_payload = get_cached_data()
    data_unavailable_for_template = False

# Default structure for the old 'aggregates' object
    template_aggregates = {
        'total_drivers': 0,
        'total_trips': 0,
        'total_sensor_data': 0, # This will be 0 if sensor API returns no data
        'invalid_sensor_data_count': 0,
        'total_valid_sensor_data': 0,
        'orphan_sensor_data_count': 0, # From your original data_service structure
        'driver_trip_sensor_stats': []
    }

    if processed_data_payload is None:
        logger.warning("Main Dashboard: No cached data available.")
        data_unavailable_for_template = True

    if processed_data_payload:
        summary_data = processed_data_payload.get("summary_totals", {})
        dashboard_metrics = processed_data_payload.get("dashboard_trip_metrics", [])

        # Map new keys from summary_data to old 'aggregates' keys
        template_aggregates['total_drivers'] = summary_data.get('total_driver_profiles_fetched_valid', 0)
        template_aggregates['total_trips'] = summary_data.get('total_trips_fetched_valid', 0)
        
        # Sensor data related totals
        # Note: Your logs show 0 sensor data fetched, so these will be 0.
        template_aggregates['total_sensor_data'] = summary_data.get('total_sensor_records_fetched_valid', 0)
        template_aggregates['invalid_sensor_data_count'] = summary_data.get('global_invalid_sensor_data_count', 0)
        template_aggregates['total_valid_sensor_data'] = summary_data.get('global_valid_sensor_data_count', 0)
        template_aggregates['orphan_sensor_data_count'] = summary_data.get('orphan_sensor_data_count', 0)
        
        # The main table data for the dashboard
        template_aggregates['driver_trip_sensor_stats'] = dashboard_metrics
        
        # Check if essential parts were still missing, to set the flag if needed
        if not summary_data or not dashboard_metrics:
            data_unavailable_for_template = True
            logger.warning("Main Dashboard: Essential data ('summary_totals' or 'dashboard_trip_metrics') missing from payload.")
    else:
        if not data_unavailable_for_template:
            logger.warning("Main Dashboard: No data payload available. Using default empty aggregates.")
        data_unavailable_for_template = True  # Ensure flag is true if payload is None

    response_headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "aggregates": template_aggregates, # Pass the reconstructed 'aggregates' object
            "data_unavailable": data_unavailable_for_template
        },
        headers=response_headers
    )
