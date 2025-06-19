# app/cache.py
import asyncio
import time
import json
import hashlib
import logging
from app.services.data_service import fetch_all_processed_data

logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 30  # seconds

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

# from app.services.data_service import fetch_all_processed_data # New import

async def refresh_cache_periodically():
    global _cached_data, _cached_checksum
    while True:
        logger.info("Refreshing cache with new data service...")
        try:
            # This single call gets all fetched, validated, and processed data
            new_data_payload = await fetch_all_processed_data()

            new_checksum = compute_checksum(new_data_payload) # compute_checksum might need to handle the new structure

            if _cached_checksum is None or new_checksum != _cached_checksum:
                _cached_data = new_data_payload
                _cached_checksum = new_checksum
                logger.info("Cache updated with new data structure (new checksum: %s)", new_checksum)
            else:
                logger.info("No change detected (checksum remains %s).", _cached_checksum)
        except Exception as e:
            logger.error("Error during cache refresh: %s", e, exc_info=True)
        await asyncio.sleep(REFRESH_INTERVAL)