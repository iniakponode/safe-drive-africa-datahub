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
    If drivers can also be huge, you can also do chunked fetch for them.
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
    1) Fetch all drivers in one go (or chunk if needed).
    2) Fetch all trips in chunks (avoid 500 error).
    3) Fetch all sensor data in chunks (avoid 500 error).

    Return a dict with lists: "drivers", "trips", "sensor_data".
    """
    async with httpx.AsyncClient() as client:
        # You can run drivers/trips/sensors concurrently if desired, 
        # but here we'll do them sequentially for clarity.

        # If you want concurrency, you can do something like:
        # d, t, s = await asyncio.gather(
        #    fetch_all_drivers(client),
        #    fetch_trips_in_chunks(client),
        #    fetch_sensor_data_in_chunks(client)
        # )

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
    Computes:
    - total_drivers
    - total_trips
    - total_sensor_data
    - trips_per_driver
    - sensor_data_per_trip
    - invalid_sensor_data_count
    """
    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])

    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)

    # trips_per_driver
    trips_per_driver = {}
    for trip in trips:
        driver_id = trip.get("driverProfileId")
        if driver_id:
            trips_per_driver[driver_id] = trips_per_driver.get(driver_id, 0) + 1

    # sensor_data_per_trip
    sensor_data_per_trip = {}
    for sensor in sensor_data:
        tid = sensor.get("trip_id")
        if tid:
            sensor_data_per_trip[tid] = sensor_data_per_trip.get(tid, 0) + 1

    # invalid sensor data
    invalid_sensor_data_count = sum(
        1 for s in sensor_data
        if s.get("x") == 0 and s.get("y") == 0 and s.get("z") == 0
    )

    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "trips_per_driver": trips_per_driver,
        "sensor_data_per_trip": sensor_data_per_trip,
        "invalid_sensor_data_count": invalid_sensor_data_count
    }
