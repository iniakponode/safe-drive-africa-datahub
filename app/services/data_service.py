# app/services/data_service.py
import asyncio
import httpx
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Backend endpoints
DRIVERS_URL = "https://api.safedriveafrica.com/api/driver_profiles/"
TRIPS_URL = "https://api.safedriveafrica.com/api/trips/"
SENSOR_URL = "https://api.safedriveafrica.com/api/raw_sensor_data/"

################################################################################
# 1) Chunked Fetch Helpers
################################################################################

async def fetch_all_drivers(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Fetch all DriverProfiles in one request (large limit)."""
    try:
        url = f"{DRIVERS_URL}?skip=0&limit=999999"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return []

async def fetch_trips_in_chunks(client: httpx.AsyncClient, chunk_size: int = 5000) -> List[Dict[str, Any]]:
    """Fetch all Trips in multiple requests until no more data."""
    all_trips = []
    skip = 0
    while True:
        try:
            url = f"{TRIPS_URL}?skip={skip}&limit={chunk_size}"
            resp = await client.get(url)
            resp.raise_for_status()
            chunk = resp.json()
        except Exception as e:
            logger.error(f"Error fetching trips (skip={skip}): {e}")
            break

        if not chunk:
            break  # no more data

        all_trips.extend(chunk)
        skip += chunk_size

    return all_trips

async def fetch_sensor_data_in_chunks(client: httpx.AsyncClient, chunk_size: int = 5000) -> List[Dict[str, Any]]:
    """Fetch all RawSensorData in multiple requests until no more data."""
    all_sensors = []
    skip = 0
    while True:
        try:
            url = f"{SENSOR_URL}?skip={skip}&limit={chunk_size}"
            resp = await client.get(url)
            resp.raise_for_status()
            chunk = resp.json()
        except Exception as e:
            logger.error(f"Error fetching sensor data (skip={skip}): {e}")
            break

        if not chunk:
            break  # no more data

        all_sensors.extend(chunk)
        skip += chunk_size

    return all_sensors

################################################################################
# 2) Master Fetch
################################################################################

async def fetch_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns:
      {
        "drivers": [...],
        "trips": [...],
        "sensor_data": [...]
      }
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
# 3) Aggregation
################################################################################

def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build summary stats + a table of per-trip sensor data.

    Output includes:
      - total_drivers
      - total_trips
      - total_sensor_data
      - invalid_sensor_data_count (global)
      - total_valid_sensor_data (global)
      - driver_trip_sensor_stats: [
          {
            "driverEmail": str,
            "tripId": str or UUID,
            "totalSensorDataCount": int,
            "invalidSensorDataCount": int,
            "validSensorDataCount": int
          }, ...
        ]
    """

    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])

    #
    #  A) driverProfileId -> email map
    #
    driver_id_to_email = {}
    for d in drivers:
        d_id = d.get("driverProfileId")
        email = d.get("email")
        if d_id and email:
            driver_id_to_email[d_id] = email

    #
    #  B) Basic totals
    #
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)

    #
    #  C) Count invalid & valid sensor data globally + per trip
    #
    invalid_sensor_data_count_global = 0
    valid_sensor_data_count_global = 0

    invalid_per_trip = {}
    valid_per_trip = {}
    sensor_data_per_trip = {}  # total # sensor rows per trip

    for s in sensor_data:
        trip_id = s.get("trip_id")
        if not trip_id:
            continue  # skip if no trip ID

        # 'values' is a list [x, y, z]
        vals = s.get("values", [])
        x = vals[0] if len(vals) > 0 else None
        y = vals[1] if len(vals) > 1 else None
        z = vals[2] if len(vals) > 2 else None

        sensor_data_per_trip[trip_id] = sensor_data_per_trip.get(trip_id, 0) + 1

        # Check if invalid
        if x == 0 and y == 0 and z == 0:
            invalid_sensor_data_count_global += 1
            invalid_per_trip[trip_id] = invalid_per_trip.get(trip_id, 0) + 1
        else:
            valid_sensor_data_count_global += 1
            valid_per_trip[trip_id] = valid_per_trip.get(trip_id, 0) + 1

    #
    #  D) Build the table: one row per trip
    #
    driver_trip_sensor_stats = []

    for t in trips:
        trip_id = t.get("id")  # or "trip_id" if that's the correct field
        driver_profile_id = t.get("driver_profile_id")

        # skip if something is missing
        if not trip_id or not driver_profile_id:
            continue

        # map driver ID -> email
        driver_email = driver_id_to_email.get(driver_profile_id, "Unknown Driver")

        # total sensor rows for this trip
        total_sensors_for_trip = sensor_data_per_trip.get(trip_id, 0)
        # invalid
        invalid_sensors_for_trip = invalid_per_trip.get(trip_id, 0)
        # valid
        valid_sensors_for_trip = valid_per_trip.get(trip_id, 0)

        row = {
            "driverEmail": driver_email,
            "tripId": trip_id,
            "totalSensorDataCount": total_sensors_for_trip,
            "invalidSensorDataCount": invalid_sensors_for_trip,
            "validSensorDataCount": valid_sensors_for_trip
        }
        driver_trip_sensor_stats.append(row)

    # sort for display consistency
    driver_trip_sensor_stats.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))

    #
    #  E) Return aggregator dict
    #
    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "invalid_sensor_data_count": invalid_sensor_data_count_global,
        "total_valid_sensor_data": valid_sensor_data_count_global,
        "driver_trip_sensor_stats": driver_trip_sensor_stats
    }
