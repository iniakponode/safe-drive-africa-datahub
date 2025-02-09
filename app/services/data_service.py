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
    2) Fetch all trips in chunks.
    3) Fetch all sensor data in chunks.

    Return a dict with lists: "drivers", "trips", "sensor_data".
    """
    async with httpx.AsyncClient() as client:
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
      - invalid_sensor_data_count (global)

    Also:
      - trips_per_driver (dict)
      - sensor_data_per_trip (dict)
      - driver_trip_sensor_stats (list of dict for the table),
        each item = {
          "driverEmail": ...,
          "tripId": ...,
          "sensorDataCount": ...,
          "invalidSensorDataCount": ...
        }
    """

    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])

    # Build a lookup from driverProfileId -> email so we can display driver email in the table
    driver_id_to_email = {}
    for d in drivers:
        driver_id = d.get("driverProfileId")
        email = d.get("email")
        if driver_id and email:
            driver_id_to_email[driver_id] = email

    # Basic totals
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)

    # Count invalid sensor data globally & also build a "invalidSensorDataPerTrip"
    invalid_sensor_data_count_global = 0
    invalid_sensor_data_per_trip = {}
    for s in sensor_data:
        t_id = s.get("trip_id")
        x, y, z = s.get("x"), s.get("y"), s.get("z")
        if x == 0 and y == 0 and z == 0:
            invalid_sensor_data_count_global += 1
            if t_id:
                invalid_sensor_data_per_trip[t_id] = invalid_sensor_data_per_trip.get(t_id, 0) + 1

    # trips_per_driver
    trips_per_driver = {}
    # sensor_data_per_trip
    sensor_data_per_trip = {}

    # For building our driver_trip_sensor_stats table
    driver_trip_sensor_stats = []

    # Build sensor_data_per_trip as well
    for s in sensor_data:
        t_id = s.get("trip_id")
        if t_id:
            sensor_data_per_trip[t_id] = sensor_data_per_trip.get(t_id, 0) + 1

    # Now iterate each trip to fill out stats for the table
    for trip in trips:
        trip_id = trip.get("id") or trip.get("trip_id")
        driver_profile_id = trip.get("driverProfileId")
        if not trip_id:
            # skip if no valid trip ID
            continue

        # For "trips_per_driver" aggregator
        if driver_profile_id:
            trips_per_driver[driver_profile_id] = trips_per_driver.get(driver_profile_id, 0) + 1

        # Build the row for the table
        driver_email = driver_id_to_email.get(driver_profile_id, "Unknown Driver")
        sensor_count = sensor_data_per_trip.get(trip_id, 0)
        invalid_count = invalid_sensor_data_per_trip.get(trip_id, 0)

        row = {
            "driverEmail": driver_email,
            "tripId": trip_id,
            "sensorDataCount": sensor_count,
            "invalidSensorDataCount": invalid_count,
        }
        driver_trip_sensor_stats.append(row)

    # Sort the rows by driverEmail, then tripId for a consistent display
    driver_trip_sensor_stats.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))

    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "invalid_sensor_data_count": invalid_sensor_data_count_global,
        "trips_per_driver": trips_per_driver,
        "sensor_data_per_trip": sensor_data_per_trip,
        "driver_trip_sensor_stats": driver_trip_sensor_stats,
    }
