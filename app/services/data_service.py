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


async def fetch_drivers(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetches ALL driver profiles (or as many as we can) by setting skip=0&limit=999999.
    """
    try:
        response = await client.get(f"{DRIVERS_URL}?skip=0&limit=999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return []


async def fetch_trips(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetches ALL trips. 
    """
    try:
        response = await client.get(f"{TRIPS_URL}?skip=0&limit=999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching trips: {e}")
        return []


async def fetch_sensor_data(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetches ALL sensor data.
    """
    try:
        response = await client.get(f"{SENSOR_URL}?skip=0&limit=99999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        return []


async def fetch_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Concurrently fetch drivers, trips, and sensor data in one go.
    """
    async with httpx.AsyncClient() as client:
        drivers, trips, sensor_data = await asyncio.gather(
            fetch_drivers(client),
            fetch_trips(client),
            fetch_sensor_data(client)
        )
    return {
        "drivers": drivers,
        "trips": trips,
        "sensor_data": sensor_data
    }


def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Aggregate the fetched data for dashboard stats:
      - total drivers, total trips, total sensor data
      - trips per driver (by email)
      - sensor data per trip
      - invalid sensor data count
    """

    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])

    # Build a lookup from driverProfileId -> email
    # so we can show "Driver Email" in the aggregator
    driver_profile_id_to_email = {}
    for d in drivers:
        driver_id = d.get("driverProfileId")  # or "id" if your field differs
        email = d.get("email")
        if driver_id and email:
            driver_profile_id_to_email[driver_id] = email

    # Basic totals
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)

    # 1) Aggregate trips per driver *email*
    trips_per_driver = {}
    for trip in trips:
        # The trip object might have "driverProfileId" referencing the driver's ID.
        driver_profile_id = trip.get("driverProfileId")
        if driver_profile_id:
            # get the email from the lookup
            driver_email = driver_profile_id_to_email.get(driver_profile_id, "Unknown Driver")
            trips_per_driver[driver_email] = trips_per_driver.get(driver_email, 0) + 1

    # 2) Aggregate sensor data per trip
    sensor_data_per_trip = {}
    for sensor in sensor_data:
        trip_id = sensor.get("trip_id")
        if trip_id:
            sensor_data_per_trip[trip_id] = sensor_data_per_trip.get(trip_id, 0) + 1

    # 3) Count invalid sensor data points (where x, y, and z == 0)
    invalid_sensor_data_count = sum(
        1 for s in sensor_data
        if s.get("x") == 0 and s.get("y") == 0 and s.get("z") == 0
    )

    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "trips_per_driver": trips_per_driver,  # keyed by email now
        "sensor_data_per_trip": sensor_data_per_trip,
        "invalid_sensor_data_count": invalid_sensor_data_count
    }