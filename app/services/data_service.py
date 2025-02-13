import asyncio
import httpx
import logging
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Backend endpoints
DRIVERS_URL = "https://api.safedriveafrica.com/api/driver_profiles/"
TRIPS_URL = "https://api.safedriveafrica.com/api/trips/"
SENSOR_URL = "https://api.safedriveafrica.com/api/raw_sensor_data/"

################################################################################
# 1) Chunked Fetch Helpers
################################################################################

async def fetch_all_drivers(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Fetch all DriverProfiles in one request (using a large limit)."""
    try:
        url = f"{DRIVERS_URL}?skip=0&limit=999999"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return []

async def fetch_trips_in_chunks(client: httpx.AsyncClient, chunk_size: int = 5000) -> List[Dict[str, Any]]:
    """Fetch all Trips in chunks until no more data is returned."""
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
    """Fetch all RawSensorData in chunks until no more data is returned."""
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
    Fetch all drivers, trips, and sensor data.
    
    Returns a dict:
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
# 3) Aggregation / Processing
################################################################################

def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build summary stats and a per-trip table.

    Returns a dict with:
      - total_drivers
      - total_trips
      - total_sensor_data
      - invalid_sensor_data_count (global)
      - total_valid_sensor_data (global)
      - driver_trip_sensor_stats: list of rows:
          {
            "driverEmail": str,
            "tripId": str or UUID,
            "totalSensorDataCount": int,
            "invalidSensorDataCount": int,
            "validSensorDataCount": int
          }
    """
    print("DEBUG: Arrived at process_data()!")
    logger.warning("TEST WARNING: This should definitely appear in the logs!")
    
    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])
    
    # Log one sample driver and one sample trip for verification.
    if drivers:
        logger.info("Sample driver object: %s", drivers[0])
    else:
        logger.info("No driver objects received.")
    
    if trips:
        logger.info("Sample trip object: %s", trips[0])
    else:
        logger.info("No trip objects received.")
    
    # A) Build a map from driverProfileId -> email.
    driver_id_to_email = {}
    for d in drivers:
        d_id = d.get("driverProfileId")
        email = d.get("email")
        if d_id and email:
            driver_id_to_email[d_id] = email
    
    # B) Compute basic totals.
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)
    
    # C) Count invalid and valid sensor data globally and per trip.
    invalid_sensor_data_count_global = 0
    valid_sensor_data_count_global = 0
    
    invalid_per_trip = {}
    valid_per_trip = {}
    sensor_data_per_trip = {}
    
    for s in sensor_data:
        trip_id = s.get("trip_id")
        if not trip_id:
            continue
        
        vals = s.get("values", [])
        x = vals[0] if len(vals) > 0 else None
        y = vals[1] if len(vals) > 1 else None
        z = vals[2] if len(vals) > 2 else None
        
        sensor_data_per_trip[trip_id] = sensor_data_per_trip.get(trip_id, 0) + 1
        
        if x == 0 and y == 0 and z == 0:
            invalid_sensor_data_count_global += 1
            invalid_per_trip[trip_id] = invalid_per_trip.get(trip_id, 0) + 1
        else:
            valid_sensor_data_count_global += 1
            valid_per_trip[trip_id] = valid_per_trip.get(trip_id, 0) + 1
    
    # D) Build the per-trip table.
    driver_trip_sensor_stats = []
    
    for idx, t in enumerate(trips, start=1):
        logger.info("Trip #%d: %s", idx, t)
        trip_id = t.get("id") or t.get("trip_id")
        driver_profile_id = t.get("driverProfileId") or t.get("driver_profile_id")
        logger.info("Extracted trip_id=%s, driver_profile_id=%s", trip_id, driver_profile_id)
        
        if not trip_id or not driver_profile_id:
            logger.warning("Skipping trip %s because trip_id or driverProfileId is missing.", t)
            continue
        
        driver_email = driver_id_to_email.get(driver_profile_id, "Unknown Driver")
        total_sensors_for_trip = sensor_data_per_trip.get(trip_id, 0)
        invalid_sensors_for_trip = invalid_per_trip.get(trip_id, 0)
        valid_sensors_for_trip = valid_per_trip.get(trip_id, 0)
        
        row = {
            "driverEmail": driver_email,
            "tripId": trip_id,
            "totalSensorDataCount": total_sensors_for_trip,
            "invalidSensorDataCount": invalid_sensors_for_trip,
            "validSensorDataCount": valid_sensors_for_trip
        }
        driver_trip_sensor_stats.append(row)
    
    driver_trip_sensor_stats.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))
    logger.info("Final driver_trip_sensor_stats (total %d rows): %s", len(driver_trip_sensor_stats), driver_trip_sensor_stats)
    
    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "invalid_sensor_data_count": invalid_sensor_data_count_global,
        "total_valid_sensor_data": valid_sensor_data_count_global,
        "driver_trip_sensor_stats": driver_trip_sensor_stats
    }

################################################################################
# 4) New Aggregation for Driver Stats
################################################################################

def process_driver_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build aggregated statistics per driver.
    For each driver (by email), compute:
      - Number of trips driven
      - Total valid sensor data count (across all trips)
      - Total invalid sensor data count (across all trips)
    
    Returns a dict:
      {
        "driver_stats": [
          {
            "driverEmail": str,
            "numTrips": int,
            "validSensorDataCount": int,
            "invalidSensorDataCount": int
          },
          ...
        ]
      }
    """
    # First, reuse the per-trip aggregation from process_data.
    aggregated = process_data(data)
    per_trip_stats = aggregated.get("driver_trip_sensor_stats", [])
    
    driver_stats = {}
    for row in per_trip_stats:
        email = row.get("driverEmail")
        if not email:
            continue
        if email not in driver_stats:
            driver_stats[email] = {
                "numTrips": 0,
                "validSensorDataCount": 0,
                "invalidSensorDataCount": 0
            }
        driver_stats[email]["numTrips"] += 1
        driver_stats[email]["validSensorDataCount"] += row.get("validSensorDataCount", 0)
        driver_stats[email]["invalidSensorDataCount"] += row.get("invalidSensorDataCount", 0)
    
    # Convert the dictionary to a list for easier template iteration.
    driver_stats_list = []
    for email, stats in driver_stats.items():
        driver_stats_list.append({
            "driverEmail": email,
            "numTrips": stats["numTrips"],
            "validSensorDataCount": stats["validSensorDataCount"],
            "invalidSensorDataCount": stats["invalidSensorDataCount"]
        })
    
    driver_stats_list.sort(key=lambda r: r["driverEmail"])
    logger.info("Final driver_stats (total %d rows): %s", len(driver_stats_list), driver_stats_list)
    
    return {
        "driver_stats": driver_stats_list
    }