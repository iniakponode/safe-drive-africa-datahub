# app/services/data_service.py
import asyncio
import httpx
import json
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
        drivers = resp.json()
        logger.info("Fetched %d driver records.", len(drivers))
        return drivers
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
            logger.info("Fetched %d trips (skip=%d).", len(chunk), skip)
        except Exception as e:
            logger.error(f"Error fetching trips (skip={skip}): {e}")
            break
        if not chunk:
            break
        all_trips.extend(chunk)
        skip += chunk_size
    logger.info("Total trips fetched: %d", len(all_trips))
    return all_trips

async def fetch_sensor_data_in_chunks(client: httpx.AsyncClient, chunk_size: int = 10000) -> List[Dict[str, Any]]:
    """Fetch all RawSensorData in chunks until no more data is returned."""
    all_sensors = []
    skip = 0
    while True:
        try:
            url = f"{SENSOR_URL}?skip={skip}&limit={chunk_size}"
            resp = await client.get(url)
            resp.raise_for_status()
            chunk = resp.json()
            logger.info("Fetched %d sensor records (skip=%d).", len(chunk), skip)
        except Exception as e:
            logger.error(f"Error fetching sensor data (skip={skip}): {e}")
            break
        if not chunk:
            break
        all_sensors.extend(chunk)
        skip += chunk_size
    logger.info("Total sensor data records fetched: %d", len(all_sensors))
    return all_sensors

################################################################################
# 2) Master Fetch
################################################################################

async def fetch_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch all drivers, trips, and sensor data.
    
    Returns a dictionary:
      {
         "drivers": [...],
         "trips": [...],
         "sensor_data": [...]
      }
    """
    async with httpx.AsyncClient() as client:
        drivers = await fetch_all_drivers(client)
        trips = await fetch_trips_in_chunks(client, chunk_size=5000)
        sensor_data = await fetch_sensor_data_in_chunks(client, chunk_size=500000)
    return {"drivers": drivers, "trips": trips, "sensor_data": sensor_data}

################################################################################
# 3) Aggregation / Processing (Per-Trip)
################################################################################

def process_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Aggregates per-trip sensor data statistics.
    
    For each trip, returns:
      - driverEmail (mapped via driverProfileId → email)
      - tripId (from "id" or "trip_id")
      - totalSensorDataCount: number of sensor records for that trip
      - invalidSensorDataCount: count of records where sensor "values" equals [0, 0, 0]
      - validSensorDataCount: remaining records
    Also returns global totals.
    Additionally, computes orphan_sensor_data_count (sensor records with no trip_id).
    """
    logger.info("DEBUG: Arrived at process_data()!")
    
    drivers = data.get("drivers", [])
    trips = data.get("trips", [])
    sensor_data = data.get("sensor_data", [])
    
    # Log sample objects.
    if drivers:
        logger.info("Sample driver object: %s", drivers[0])
    else:
        logger.info("No driver objects received.")
    if trips:
        logger.info("Sample trip object: %s", trips[0])
    else:
        logger.info("No trip objects received.")
    
    # A) Build mapping: driverProfileId -> email.
    driver_id_to_email = {}
    for d in drivers:
        d_id = d.get("driverProfileId")
        email = d.get("email")
        if d_id and email:
            driver_id_to_email[d_id] = email
    
    # B) Global totals.
    total_drivers = len(drivers)
    total_trips = len(trips)
    total_sensor_data = len(sensor_data)
    
    # Compute orphan sensor records (those without a trip_id)
    orphan_sensor_data = [s for s in sensor_data if not s.get("trip_id")]
    orphan_sensor_data_count = len(orphan_sensor_data)
    logger.info("Orphan sensor data count: %d", orphan_sensor_data_count)
    
    # C) Count sensor records per trip (only for records with a valid trip_id).
    invalid_sensor_data_count_global = 0
    valid_sensor_data_count_global = 0
    invalid_per_trip = {}
    valid_per_trip = {}
    sensor_data_per_trip = {}
    
    for s in sensor_data:
        trip_id = s.get("trip_id")
        if not trip_id:
            continue  # Skip orphan records for per-trip aggregation.
        # Ensure the "values" field is a list.
        vals = s.get("values", [])
        if isinstance(vals, str):
            try:
                vals = json.loads(vals)
            except Exception as e:
                logger.error("Error parsing sensor values for record %s: %s", s, e)
                vals = []
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
    
    # D) Build per-trip table.
    driver_trip_sensor_stats = []
    for idx, t in enumerate(trips, start=1):
        logger.info("Trip #%d: %s", idx, t)
        trip_id = t.get("id") or t.get("trip_id") or 0
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
        "orphan_sensor_data_count": orphan_sensor_data_count,
        "invalid_sensor_data_count": invalid_sensor_data_count_global,
        "total_valid_sensor_data": valid_sensor_data_count_global,
        "driver_trip_sensor_stats": driver_trip_sensor_stats
    }

################################################################################
# 4) Aggregation for Driver-Level Stats
################################################################################

def process_driver_data(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Aggregates per-driver statistics from per-trip data.
    For each driver (by email), computes:
      - Number of trips driven
      - Total valid sensor data count (across all trips)
      - Total invalid sensor data count (across all trips)
    Drivers with no trips are included with 0 values.
    
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
         ],
         "total_num_trips": int,
         "total_valid_sensor_data": int,
         "total_invalid_sensor_data": int
      }
    """
    aggregated = process_data(data)
    per_trip_stats = aggregated.get("driver_trip_sensor_stats", [])
    
    # Build mapping for all drivers from the drivers list.
    drivers = data.get("drivers", [])
    driver_id_to_email = {}
    for d in drivers:
        d_id = d.get("driverProfileId")
        email = d.get("email")
        if d_id and email:
            driver_id_to_email[d_id] = email
    
    # Initialize driver_stats for every driver.
    driver_stats = {}
    for d_id, email in driver_id_to_email.items():
        driver_stats[email] = {"numTrips": 0, "validSensorDataCount": 0, "invalidSensorDataCount": 0}
    
    # Aggregate per-trip stats into driver_stats.
    for row in per_trip_stats:
        email = row.get("driverEmail")
        if email in driver_stats:
            driver_stats[email]["numTrips"] += 1
            driver_stats[email]["validSensorDataCount"] += row.get("validSensorDataCount", 0)
            driver_stats[email]["invalidSensorDataCount"] += row.get("invalidSensorDataCount", 0)
        else:
            driver_stats[email] = {
                "numTrips": 1,
                "validSensorDataCount": row.get("validSensorDataCount", 0),
                "invalidSensorDataCount": row.get("invalidSensorDataCount", 0)
            }
    
    driver_stats_list = []
    totalTrips = 0
    totalValid = 0
    totalInvalid = 0
    for email, stats in driver_stats.items():
        totalTrips += stats["numTrips"]
        totalValid += stats["validSensorDataCount"]
        totalInvalid += stats["invalidSensorDataCount"]
        driver_stats_list.append({
            "driverEmail": email,
            "numTrips": stats["numTrips"],
            "validSensorDataCount": stats["validSensorDataCount"],
            "invalidSensorDataCount": stats["invalidSensorDataCount"]
        })
    
    driver_stats_list.sort(key=lambda r: r["driverEmail"])
    logger.info("Final driver_stats (total %d rows): %s", len(driver_stats_list), driver_stats_list)
    
    return {
        "driver_stats": driver_stats_list,
        "total_num_trips": totalTrips,
        "total_valid_sensor_data": totalValid,
        "total_invalid_sensor_data": totalInvalid
    }
