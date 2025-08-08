# src/cache.py

import time
import asyncio
from typing import Dict, Any

# A simple in-memory cache stored as a global dictionary.
_CACHE: Dict[str, Any] = {}
_LOCK = asyncio.Lock()
_TTL_SECONDS = 3600  # Cache entries will expire after 1 hour

async def set_json(key: str, data: dict):
    """Saves data to the in-memory cache with a timestamp."""
    async with _LOCK:
        _CACHE[key] = {
            "data": data,
            "timestamp": time.time()
        }
    print(f"INFO: Cached data for key '{key}'.")

async def get_json(key: str) -> dict | None:
    """Retrieves data from the in-memory cache, checking for expiration."""
    entry = _CACHE.get(key)
    if entry:
        if (time.time() - entry["timestamp"]) < _TTL_SECONDS:
            return entry["data"]
        else:
            # Clean up expired entry
            async with _LOCK:
                _CACHE.pop(key, None)
            print(f"INFO: Expired cache entry for key '{key}' removed.")
            return None
    return None