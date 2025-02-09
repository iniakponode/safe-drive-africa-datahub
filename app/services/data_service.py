# app/services/data_service.py
import asyncio
import httpx
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Define your base API endpoints.
DRIVERS_URL = "https://api.safedriveafrica.com/api/driver_profiles/"
# We'll call this endpoint later: /driver-profiles/by-profile-id/{email}?limit_sensor_data=999999
NESTED_URL = "https://api.safedriveafrica.com/api/driver-profiles/by-profile-id"

################################################################################
# 1) Fetch the high-level list of ALL driver profiles.
################################################################################

async def fetch_all_drivers(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetches ALL driver profiles (or as many as we can) by setting skip=0&limit=999999.
    Returns a list of driver profile objects, each presumably containing:
      {
         "driverProfileId": ...,
         "email": ...,
         "sync": ...
      }
    """
    try:
        url = f"{DRIVERS_URL}?skip=0&limit=999999"
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching drivers list: {e}")
        return []

################################################################################
# 2) For each driver, fetch nested data via /driver-profiles/by-profile-id/{email}.
################################################################################

async def fetch_driver_details(client: httpx.AsyncClient, email: str) -> Dict[str, Any]:
    """
    Calls /api/driver-profiles/by-profile-id/{email}?limit_sensor_data=999999
    Returns a structure that includes:
      {
        "driverProfileId": ...,
        "email": ...,
        "trips": [
           {
             "id": ...,
             "tripId": ...,
             "raw_sensor_data": [
               { "x": ..., "y": ..., "z": ..., ... },
               ...
             ]
           },
           ...
        ]
      }
    """
    try:
        url = f"{NESTED_URL}/{email}?limit_sensor_data=999999"  # override limit to fetch all sensor data
        response = await client.get(url)
        response.raise_for_status()
        return response.json()  # driverProfileOut
    except httpx.HTTPStatusError as http_err:
        logger.error(f"Driver detail fetch failed for {email}: {http_err}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching driver details for {email}: {e}")
        return {}

################################################################################
# 3) Orchestrate the data fetching: 
#    - get the base list of drivers
#    - for each driver, fetch the nested details
################################################################################

async def fetch_all_data() -> List[Dict[str, Any]]:
    """
    Returns a list of 'full' driver objects, each containing
    {
       "driverProfileId": ...,
       "email": ...,
       "trips": [
           {
               "id": ...,
               "raw_sensor_data": [...]
           },
           ...
       ]
    }
    """
    async with httpx.AsyncClient() as client:
        drivers_list = await fetch_all_drivers(client)

        # gather calls to fetch_driver_details for each driver’s email
        tasks = []
        for d in drivers_list:
            email = d.get("email")
            if email:
                tasks.append(fetch_driver_details(client, email))

        # Run them concurrently
        all_driver_details = await asyncio.gather(*tasks)

    # all_driver_details will be a list of dicts (one per driver),
    # each containing driverProfile + trips + sensor data.
    # Some entries might be empty if the fetch failed or if no details found.
    return all_driver_details

################################################################################
# 4) Process the aggregated data:
#    - total drivers, total trips, total sensor data
#    - invalid sensor data
#    - driver_trip_sensor_stats: for each trip of each driver
################################################################################

def process_data(driver_details_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a list of driver detail objects (each includes trips and raw sensor data),
    build a global summary + per-trip breakdown.

    Return structure:
      {
        "total_drivers": int,
        "total_trips": int,
        "total_sensor_data": int,
        "invalid_sensor_data_count": int,
        "driver_trip_sensor_stats": [
            {
              "driverEmail": str,
              "tripId": str or int,
              "sensorDataCount": int,
              "invalidSensorDataCount": int
            }, ...
        ]
      }
    """

    # Basic counters
    total_drivers = 0
    total_trips = 0
    total_sensor_data = 0
    invalid_sensor_data_count = 0

    # We'll accumulate a row for each trip (per driver)
    driver_trip_sensor_stats = []

    for driver_info in driver_details_list:
        if not driver_info:
            # skip empty/invalid entries
            continue

        driver_email = driver_info.get("email", "Unknown Email")
        trips = driver_info.get("trips", [])
        total_drivers += 1  # each item in driver_details_list is a unique driver

        # For each trip, count total sensor data points + invalid points
        for t in trips:
            trip_id = t.get("id") or t.get("tripId") or "Unknown Trip"
            raw_sensor_data = t.get("raw_sensor_data", [])

            # track how many sensor records in this trip
            sensor_count = len(raw_sensor_data)
            total_sensor_data += sensor_count

            # count invalid sensor data
            invalid_count = sum(
                1
                for s in raw_sensor_data
                if s.get("x") == 0 and s.get("y") == 0 and s.get("z") == 0
            )
            invalid_sensor_data_count += invalid_count

            # Build a row for the breakdown table
            row = {
                "driverEmail": driver_email,
                "tripId": trip_id,
                "sensorDataCount": sensor_count,
                "invalidSensorDataCount": invalid_count,
            }
            driver_trip_sensor_stats.append(row)

        total_trips += len(trips)

    # Sort breakdown if you like (by driver email, then trip ID)
    driver_trip_sensor_stats.sort(key=lambda r: (r["driverEmail"], str(r["tripId"])))

    return {
        "total_drivers": total_drivers,
        "total_trips": total_trips,
        "total_sensor_data": total_sensor_data,
        "invalid_sensor_data_count": invalid_sensor_data_count,
        "driver_trip_sensor_stats": driver_trip_sensor_stats,
    }