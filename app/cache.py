# app/cache.py
import asyncio
import time
import json
import hashlib
import logging
from app.services.data_service import fetch_all_data, process_data, process_driver_data

logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 10  # seconds

_cached_data = None  
_cached_checksum = None

def get_cached_data():
    """Return the latest cached data."""
    return _cached_data

def compute_checksum(data: dict) -> str:
    """Compute an MD5 checksum of the given data (JSON serialized with sorted keys)."""
    try:
        # Convert the data to a JSON string with sorted keys.
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error("Error computing checksum: %s", e)
        return ""

async def refresh_cache_periodically():
    global _cached_data, _cached_checksum
    while True:
        logger.info("Refreshing cache...")
        try:
            raw_data = await fetch_all_data()
            aggregated = process_data(raw_data)
            driver_stats = process_driver_data(raw_data)
            new_cache = {"aggregates": aggregated, "driver_stats": driver_stats}
            new_checksum = compute_checksum(new_cache)
            if _cached_checksum is None or new_checksum != _cached_checksum:
                _cached_data = new_cache
                _cached_checksum = new_checksum
                logger.info("Cache updated (new checksum: %s)", new_checksum)
            else:
                logger.info("No change detected (checksum remains %s).", _cached_checksum)
        except Exception as e:
            logger.error("Error during cache refresh: %s", e)
        await asyncio.sleep(REFRESH_INTERVAL)