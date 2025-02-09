# app/services/data_service.py
import asyncio
import httpx
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Define the backend API endpoints.
DRIVERS_URL = "https://api.safedriveafrica.com/api/driver_profiles/"
TRIPS_URL = "https://api.safedriveafrica.com/api/trips/"
SENSOR_URL = "https://api.safedriveafrica.com/api/raw_sensor_data/"

################################################################################
# PAGINATION HELPERS
################################################################################

async def fetch_all_drivers(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetches ALL driver profiles (with a large limit in one request).
    """
    try:
        url = f"{DRIVERS_URL}?skip=0&limit=999999"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return []

async def fetch_trips_in_chunks(client: httpx.AsyncClient, chunk_size: int = 5000) -> List[Dict[str, Any]]:
    """
    Fetch all trips in multiple requests of `chunk_size` each.
    Continues until an empty chunk is returned.
    """
    all_trips = []
    skip = 0

    while True:
        try:
            url = f"{TRIPS_URL}?skip={skip}&limit={chunk_size}"
            resp = await client.get(url)
            resp.raise_for_status()
            chunk = resp.json()
        except Exception as e:
            logger.error(f"Error fetching trips (page skip={skip}): {e}")
            break

        if not chunk:
            # No more trips
            break

        all_trips.extend(chunk)
        skip += chunk_size

    return all_trips

async def fetch_sensor_data_in_chunks(client: httpx.AsyncClient, chunk_size: int = 5000) -> List[Dict[str, Any]]:
    """
    Fetch all sensor data in multiple requests of `chunk_size` each.
    Continues until an empty chunk is returned.
    """
    all_sensors = []
    skip = 0

    while True:
        try:
            url = f"{SENSOR_URL}?skip={skip}&limit={chunk_size}"
            resp = await client.get(url)
            resp.raise_for_status()
            chunk = resp.json()
        except Exception as e:
            logger.error(f"Error fetching sensor data (page skip={skip}): {e}")
            break

        if not chunk:
            # No more sensor data
            break

        all_sensors.extend(chunk)
        skip += chunk_size

    return all_sensors

################################################################################
# MASTER FETCH
################################################################################

async def fetch_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    1) Fetch all drivers (one large request).
    2) Fetch all trips in chunks.
    3) Fetch all sensor data in chunks.
    Returns { "drivers": [...], "trips": [...], "sensor_data": [...] }
    """
    async with httpx.AsyncClient() as client:
        drivers = await fetch_all_drivers(client)
        trips = await fetch_trips_in_chunks(client, chunk_size=5000)
        sensor_data = await fetch_sensor_data_in_chunks(client, chunk_size=5000)

    return {
        "drivers": drivers,
        "trips": trips,
        "sensor_data": sensor_data
    }

################################################################################
# AGGREGATION
################################################################################

def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Aggregates data from:
      - "drivers": list of DriverProfile JSON (with driverProfileId, email, etc.)
      - "trips": list of Trip JSON (with id, driverProfileId, etc.)
      - "sensor_data": list of RawSensorData JSON (with trip_id, values=[x,y,z], etc.)

    Returns a dict with:
      - total_drivers, total_trips, total_sensor_data
      - invalid_sensor_data_count (global)
      - driver_trip_sensor_stats: list of {driverEmail, tripId, sensorDataCount, invalidSensorDataCount}
    """

    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])

    # 1) Build a map driverProfileId -> email to display driver emails in table
    driver_id_to_email = {}
    for d in drivers:
        driver_id = d.get("driverProfileId")
        email = d.get("email")
        if driver_id and email:
            driver_id_to_email[driver_id] = email

    # 2) Basic total counts
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)

    # 3) We'll track invalid sensor data globally + per trip
    invalid_sensor_data_count_global = 0
    invalid_per_trip = {}

    # We'll also track how many sensor points each trip has
    sensor_data_per_trip = {}

    # 4) Parse each sensor record: check if values=[0.0,0.0,0.0]
    for s in sensor_data:
        trip_id = s.get("trip_id")
        vals = s.get("values", [])  # e.g. [0.0, 0.0, 0.0]
        
        # Make sure we don't crash if it's not exactly 3 elements
        x = vals[0] if len(vals) > 0 else None
        y = vals[1] if len(vals) > 1 else None
        z = vals[2] if len(vals) > 2 else None

        # Count total sensor records for this trip
        sensor_data_per_trip[trip_id] = sensor_data_per_trip.get(trip_id, 0) + 1

        # Check if it's "invalid" (x=0,y=0,z=0)
        if x == 0.0 and y == 0.0 and z == 0.0:
            invalid_sensor_data_count_global += 1
            if trip_id:
                invalid_per_trip[trip_id] = invalid_per_trip.get(trip_id, 0) + 1

    # 5) Build a "driver_trip_sensor_stats" table
    driver_trip_sensor_stats = []
    for t in trips:
        trip_id = t.get("id")
        driver_profile_id = t.get("driverProfileId")

        # If we don't have an ID or driverProfileId, skip
        if not trip_id or not driver_profile_id:
            continue

        # Get the driver's email from our map
        driver_email = driver_id_to_email.get(driver_profile_id, "Unknown Driver")

        # total # of sensor records for this trip
        total_sensors_for_trip = sensor_data_per_trip.get(trip_id, 0)
        # how many of those were invalid
        invalid_sensors_for_trip = invalid_per_trip.get(trip_id, 0)

        row = {
            "driverEmail": driver_email,
            "tripId": trip_id,
            "sensorDataCount": total_sensors_for_trip,
            "invalidSensorDataCount": invalid_sensors_for_trip,
        }
        driver_trip_sensor_stats.append(row)

    # Sort rows for a cleaner display
    driver_trip_sensor_stats.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))

    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "invalid_sensor_data_count": invalid_sensor_data_count_global,
        "driver_trip_sensor_stats": driver_trip_sensor_stats,
    }