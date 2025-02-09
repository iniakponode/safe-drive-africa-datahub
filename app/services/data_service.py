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
    try:
        response = await client.get(DRIVERS_URL + "?skip=0&limit=999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return []

async def fetch_trips(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    try:
        response = await client.get(TRIPS_URL+ "?skip=0&limit=999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching trips: {e}")
        return []

async def fetch_sensor_data(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    try:
        response = await client.get(SENSOR_URL+ "?skip=0&limit=99999999")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        return []

async def fetch_all_data() -> Dict[str, List[Dict[str, Any]]]:
    async with httpx.AsyncClient() as client:
        drivers, trips, sensor_data = await asyncio.gather(
            fetch_drivers(client),
            fetch_trips(client),
            fetch_sensor_data(client)
        )
    return {"drivers": drivers, "trips": trips, "sensor_data": sensor_data}

def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])
    
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)
    
    # Aggregate trips per driver (assuming each trip record contains "driver_profile_id")
    trips_per_driver = {}
    for trip in trips:
        driver_id = trip.get("driverProfileId")
        if driver_id:
            trips_per_driver[driver_id] = trips_per_driver.get(driver_id, 0) + 1

    # Aggregate sensor data per trip (assuming each sensor record contains "trip_id")
    sensor_data_per_trip = {}
    for sensor in sensor_data:
        trip_id = sensor.get("trip_id")
        if trip_id:
            sensor_data_per_trip[trip_id] = sensor_data_per_trip.get(trip_id, 0) + 1

    # Count invalid sensor data points (where x, y, and z are all zero)
    invalid_sensor_data_count = sum(
        1 for sensor in sensor_data
        if sensor.get("x") == 0 and sensor.get("y") == 0 and sensor.get("z") == 0
    )
    
    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "trips_per_driver": trips_per_driver,
        "sensor_data_per_trip": sensor_data_per_trip,
        "invalid_sensor_data_count": invalid_sensor_data_count
    }
