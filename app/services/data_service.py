# app/services/data_service.py
import asyncio
import httpx
import json
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationInfo, field_validator, ValidationError

# --- Configuration ---
logging.basicConfig(level=logging.INFO) # Adjust level as needed
logger = logging.getLogger(__name__)

DRIVERS_URL = "https://api.safedriveafrica.com/api/driver_profiles/"
TRIPS_URL = "https://api.safedriveafrica.com/api/trips/"
SENSOR_URL = "https://api.safedriveafrica.com/api/raw_sensor_data/"

# --- Pydantic Models for Data Validation ---

class BaseApiModel(BaseModel):
    class Config:
        extra = 'ignore' # Ignore extra fields from API not defined in model

    @classmethod
    def strip_empty_str(cls, v: Any) -> Optional[Any]:
        if isinstance(v, str) and not v.strip():
            return None
        return v

class DriverProfileModel(BaseApiModel):
    driverProfileId: str
    email: Optional[str] = None
    # name: Optional[str] = None # Example: Add other fields you care about

    @field_validator('driverProfileId', 'email', mode='before')
    @classmethod
    def normalize_and_strip_fields(cls, v: Any, info: ValidationInfo): # info can be used for field_name if needed
        """
        Normalizes string fields: strips whitespace, converts empty strings to None.
        """
        if isinstance(v, str):
            stripped_v = v.strip() # This will handle newlines like 'gzkzof\n' -> 'gzkzof'
                                  # and spaces like 'Lucky ' -> 'Lucky'
            if not stripped_v:    # If string becomes empty after stripping
                return None       # Convert to None
            return stripped_v     # Return the cleaned, non-empty string
        return v # Return non-string values as is (Pydantic will type-check them)

class TripModel(BaseApiModel):
    # Assuming 'id' or 'trip_id' is the trip's own identifier
    # We'll handle potential aliasing during raw data parsing
    trip_id: str
    driverProfileId: Optional[str] = None

    @field_validator('trip_id', 'driverProfileId', mode='before')
    @classmethod
    def normalize_empty_strings_to_none(cls, v: Any, info: ValidationInfo): # info can be useful for context if needed
        # info.field_name will tell you if it's 'trip_id' or 'driverProfileId'
        if isinstance(v, str):
            stripped_v = v.strip()
            if not stripped_v: # If empty after stripping
                # For 'trip_id' which is 'str' (not Optional), returning None here
                # will correctly cause a validation error later if it was an empty string.
                # For 'driverProfileId' which is 'Optional[str]', None is acceptable.
                return None
            return stripped_v # Return the stripped, non-empty string
        return v # Return other types as is (Pydantic will type check later)

class SensorValueItemModel(BaseModel):
    # Define if sensor values have a specific structure, otherwise use List[float]
    # For simplicity, assuming List[float] for now.
    pass

class SensorDataModel(BaseApiModel):
    # We'll handle potential aliasing for trip_id during raw data parsing
    trip_id: Optional[str] = None
    values: List[Union[float, int]] = [] # Allow int or float

    _normalize_trip_id = field_validator('trip_id', mode='before')(BaseApiModel.strip_empty_str)

    @field_validator('values', mode='before')
    @classmethod
    def parse_sensor_values(cls, v: Any) -> List[Union[float, int]]:
        if isinstance(v, str):
            try:
                parsed_v = json.loads(v)
            except json.JSONDecodeError:
                logger.warning(f"Sensor values: Could not JSON decode string: {v}")
                return []
        elif isinstance(v, list):
            parsed_v = v
        else:
            logger.warning(f"Sensor values: Unexpected type: {type(v)}, value: {v}")
            return []

        if not isinstance(parsed_v, list):
            logger.warning(f"Sensor values: Parsed value is not a list: {parsed_v}")
            return []
        
        numeric_values = []
        for item in parsed_v:
            try:
                numeric_values.append(float(item)) # Convert all to float for consistency
            except (ValueError, TypeError):
                logger.warning(f"Sensor values: Could not convert item to float: {item}")
                # Decide: skip item, use a default, or make the whole list invalid
        return numeric_values


# --- Data Fetching (with Pydantic Validation) ---

async def fetch_and_validate_data(
    client: httpx.AsyncClient,
    url: str,
    model: BaseModel,
    paged: bool = False,
    chunk_size: int = 1000,
    limit_param_name: str = "limit",
    skip_param_name: str = "skip",
    is_profile_api: bool = False
) -> List[BaseModel]:
    validated_items = []
    raw_items_count = 0
    validation_error_count = 0
    
    if not paged:
        try:
            # For drivers, try to fetch all, but be wary of API limits
            # The `999999` limit might need to be adjusted if the API has a lower hard cap
            fetch_url = f"{url}?{skip_param_name}=0&{limit_param_name}=999999" if is_profile_api else url
            logger.info(f"Fetching data from {fetch_url}")
            resp = await client.get(fetch_url)
            resp.raise_for_status()
            raw_json_list = resp.json()
            if not isinstance(raw_json_list, list):
                logger.error(f"Expected a list from {fetch_url}, got {type(raw_json_list)}")
                return []
            
            raw_items_count = len(raw_json_list)
            for idx, item_data in enumerate(raw_json_list):
                try:
                    # Handle potential aliasing for trip_id ('id' vs 'trip_id')
                    if model == TripModel and 'id' in item_data and 'trip_id' not in item_data:
                        item_data['trip_id'] = item_data.pop('id')
                    validated_items.append(model.model_validate(item_data))
                except ValidationError as e:
                    validation_error_count += 1
                    logger.warning(f"Validation error for item #{idx} from {url}: {e.errors()} - Data: {item_data}")
        except Exception as e:
            logger.error(f"Error fetching non-paged data from {url}: {e}", exc_info=True)
    else: # Paged fetching
        skip = 0
        while True:
            try:
                fetch_url = f"{url}?{skip_param_name}={skip}&{limit_param_name}={chunk_size}"
                logger.info(f"Fetching paged data from {fetch_url}")
                resp = await client.get(fetch_url)
                resp.raise_for_status()
                raw_json_list = resp.json()
                if not isinstance(raw_json_list, list):
                    logger.error(f"Expected a list from {fetch_url}, got {type(raw_json_list)}")
                    break
                
                if not raw_json_list:
                    break # No more data

                page_raw_items_count = len(raw_json_list)
                raw_items_count += page_raw_items_count
                page_validation_error_count = 0

                for item_data in raw_json_list:
                    try:
                        # Handle potential aliasing for trip_id ('id' vs 'trip_id')
                        # and sensor_data's trip_id ('trip_id' might be directly available)
                        if model == TripModel and 'id' in item_data and 'trip_id' not in item_data:
                            item_data['trip_id'] = item_data.pop('id')
                        # No specific aliasing needed for SensorDataModel here if 'trip_id' is the field name
                        validated_items.append(model.model_validate(item_data))
                    except ValidationError as e:
                        page_validation_error_count += 1
                        logger.warning(f"Validation error for item from {fetch_url} (skip {skip}): {e.errors()} - Data: {item_data}")
                validation_error_count += page_validation_error_count
                skip += page_raw_items_count
            except Exception as e:
                logger.error(f"Error fetching paged data from {url} (skip {skip}): {e}", exc_info=True)
                break
                
    logger.info(f"Fetched from {url}: {raw_items_count} raw items, {len(validated_items)} successfully validated items, {validation_error_count} validation errors.")
    return validated_items


async def fetch_all_processed_data() -> Dict[str, Any]:
    """
    Fetches all raw data, validates it, and then processes it into aggregated forms.
    This is the main function to be called by the caching layer or directly by routes if cache is empty.
    """
    async with httpx.AsyncClient(timeout=30.0) as client: # Increased timeout
        drivers_list: List[DriverProfileModel] = await fetch_and_validate_data(client, DRIVERS_URL, DriverProfileModel, is_profile_api=True)
        trips_list: List[TripModel] = await fetch_and_validate_data(client, TRIPS_URL, TripModel, paged=True, chunk_size=5000)
        sensor_data_list: List[SensorDataModel] = await fetch_and_validate_data(client, SENSOR_URL, SensorDataModel, paged=True, chunk_size=10000)

    return process_and_aggregate_data(drivers_list, trips_list, sensor_data_list)


# --- Unified Data Processing and Aggregation ---

def process_and_aggregate_data(
    valid_drivers: List[DriverProfileModel],
    valid_trips: List[TripModel],
    valid_sensor_data: List[SensorDataModel]
) -> Dict[str, Any]:
    logger.info(f"Processing data: {len(valid_drivers)} valid drivers, {len(valid_trips)} valid trips, {len(valid_sensor_data)} valid sensor data records.")

    # 1. Create driver lookup map (from validated drivers)
    #    Using driverProfileId as key.
    drivers_map: Dict[str, DriverProfileModel] = {
        driver.driverProfileId: driver for driver in valid_drivers if driver.driverProfileId
    }
    if len(drivers_map) != len(valid_drivers):
        logger.warning(f"Some valid driver profiles had missing driverProfileId after validation. Count: {len(valid_drivers) - len(drivers_map)}")


    # 2. Process sensor data: group by trip_id and count valid/invalid
    sensor_stats_by_trip: Dict[str, Dict[str, int]] = {} # trip_id -> {total:X, valid:Y, invalid:Z}
    orphan_sensor_data_count = 0
    total_sensor_records_processed = 0
    invalid_sensor_data_global = 0
    valid_sensor_data_global = 0

    for sensor in valid_sensor_data:
        total_sensor_records_processed +=1
        if not sensor.trip_id:
            orphan_sensor_data_count += 1
            continue

        stats = sensor_stats_by_trip.setdefault(sensor.trip_id, {"total": 0, "valid": 0, "invalid": 0})
        stats["total"] += 1
        
        # Assuming [0,0,0] or empty list means invalid for sensor values
        if not sensor.values or all(v == 0 for v in sensor.values):
            stats["invalid"] += 1
            invalid_sensor_data_global +=1
        else:
            stats["valid"] += 1
            valid_sensor_data_global +=1
            
    logger.info(f"Sensor data processed. Orphaned sensor records: {orphan_sensor_data_count}. Stats calculated for {len(sensor_stats_by_trip)} trips.")

    # 3. Build driver_trip_sensor_stats (for dashboard table)
    driver_trip_sensor_stats_list: List[Dict[str, Any]] = []
    trips_processed_for_dashboard = 0
    trips_skipped_no_driver_id_in_trip = 0
    trips_with_unmapped_driver_id = 0

    for trip in valid_trips:
        if not trip.trip_id: # Should have been caught by validation, but double check
            logger.warning(f"Encountered valid trip with no trip_id: {trip}, skipping for dashboard stats.")
            continue

        driver_email_display = "Unknown Driver (Data Issue)" # Default
        
        if trip.driverProfileId:
            driver_profile = drivers_map.get(trip.driverProfileId)
            if driver_profile:
                driver_email_display = driver_profile.email or f"Driver ID: {driver_profile.driverProfileId} (Email Missing)"
            else:
                # DriverProfileId from trip not found in our fetched driver profiles
                driver_email_display = f"Unknown Driver (Profile ID: {trip.driverProfileId} Not Found)"
                trips_with_unmapped_driver_id +=1
        else:
            # driverProfileId is missing from the trip record itself
            driver_email_display = "Unknown Driver (Trip Missing Driver ID)"
            trips_skipped_no_driver_id_in_trip += 1
            # Decide if these trips should even be in driver_trip_sensor_stats or logged separately.
            # For now, they are included to show the trip happened but couldn't be linked well.

        trip_sensor_info = sensor_stats_by_trip.get(trip.trip_id, {"total": 0, "valid": 0, "invalid": 0})

        driver_trip_sensor_stats_list.append({
            "driverEmail": driver_email_display, # This provides more context than just "Unknown Driver"
            "driverProfileId": trip.driverProfileId,
            "tripId": trip.trip_id,
            "totalSensorDataCount": trip_sensor_info["total"],
            "invalidSensorDataCount": trip_sensor_info["invalid"],
            "validSensorDataCount": trip_sensor_info["valid"]
        })
        trips_processed_for_dashboard +=1

    logger.info(f"Built driver_trip_sensor_stats for dashboard: {trips_processed_for_dashboard} trips included.")
    if trips_skipped_no_driver_id_in_trip > 0:
        logger.warning(f"{trips_skipped_no_driver_id_in_trip} trips had a missing driverProfileId in the trip record itself.")
    if trips_with_unmapped_driver_id > 0:
        logger.warning(f"{trips_with_unmapped_driver_id} trips had a driverProfileId that was not found among the fetched driver profiles.")

    driver_trip_sensor_stats_list.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))


    # 4. Build driver_stats (for /drivers page)
    #    Ensure ALL validly fetched drivers get a row, even if email is missing or they have no trips.
    driver_summary_stats_map: Dict[str, Dict[str, Any]] = {}

    for driver_id, profile in drivers_map.items():
        # Use email as primary key for display if available, otherwise use a placeholder with ID
        display_key = profile.email or f"Driver ID: {profile.driverProfileId} (Email Missing)"
        driver_summary_stats_map[display_key] = {
            "numTrips": 0,
            "validSensorDataCount": 0,
            "invalidSensorDataCount": 0
            # "driverProfileId": profile.driverProfileId # Optionally include for reference
        }
    
    # Aggregate trip data into the driver_summary_stats_map
    for trip_stat_row in driver_trip_sensor_stats_list:
        # The driverEmail here is already determined (actual email, placeholder, or various "Unknown")
        key = trip_stat_row["driverEmail"]
        
        if key not in driver_summary_stats_map:
            # This case handles trips assigned to "Unknown Driver (Trip Missing Driver ID)"
            # or "Unknown Driver (Profile ID: X Not Found)" if these weren't pre-initialized
            # (they wouldn't be if they don't correspond to a valid fetched driver profile).
            logger.info(f"Creating new entry in driver_summary_stats_map for key from trip: {key}")
            driver_summary_stats_map[key] = {"numTrips": 0, "validSensorDataCount": 0, "invalidSensorDataCount": 0}

        driver_summary_stats_map[key]["numTrips"] += 1
        driver_summary_stats_map[key]["validSensorDataCount"] += trip_stat_row["validSensorDataCount"]
        driver_summary_stats_map[key]["invalidSensorDataCount"] += trip_stat_row["invalidSensorDataCount"]

    final_driver_stats_list = []
    total_aggregated_trips = 0
    for display_email_or_id, stats in driver_summary_stats_map.items():
        final_driver_stats_list.append({
            "driverEmail": display_email_or_id, # This is the key used for display
            "numTrips": stats["numTrips"],
            "validSensorDataCount": stats["validSensorDataCount"],
            "invalidSensorDataCount": stats["invalidSensorDataCount"]
        })
        total_aggregated_trips += stats["numTrips"]
        
    final_driver_stats_list.sort(key=lambda r: r["driverEmail"])
    logger.info(f"Built final_driver_stats_list for /drivers page: {len(final_driver_stats_list)} unique driver entries.")

    return {
        "summary_totals": {
            "total_driver_profiles_fetched_valid": len(valid_drivers),
            "total_trips_fetched_valid": len(valid_trips),
            "total_trips_processed_for_dashboard": trips_processed_for_dashboard,
            "trips_skipped_no_driver_id_in_trip_record": trips_skipped_no_driver_id_in_trip,
            "trips_with_unmapped_driver_id": trips_with_unmapped_driver_id,
            "total_sensor_records_fetched_valid": len(valid_sensor_data),
            "orphan_sensor_data_count": orphan_sensor_data_count,
            "global_invalid_sensor_data_count": invalid_sensor_data_global,
            "global_valid_sensor_data_count": valid_sensor_data_global,
            "total_aggregated_trips_in_driver_stats": total_aggregated_trips,
        },
        "dashboard_trip_metrics": driver_trip_sensor_stats_list, # Formerly "driver_trip_sensor_stats"
        "driver_focused_stats": { # Formerly just "driver_stats" which was a list. Now a dict.
            "driver_list": final_driver_stats_list, # The list of drivers for the table
            "total_num_trips": sum(item['numTrips'] for item in final_driver_stats_list), # Recalculate for this list
            "total_valid_sensor_data": sum(item['validSensorDataCount'] for item in final_driver_stats_list),
            "total_invalid_sensor_data": sum(item['invalidSensorDataCount'] for item in final_driver_stats_list),
        }
    }