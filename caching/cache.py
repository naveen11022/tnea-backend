import os
import logging
import json
from typing import Any, Optional
from dotenv import load_dotenv
import redis

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEFAULT_TTL = int(os.getenv("CACHE_TTL", "3600"))

try:
    redis_client: Optional[redis.Redis] = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    redis_client.ping()
    logger.info("Connected to Redis at %s", REDIS_URL)
except Exception as exc:
    logger.warning("Redis unavailable (%s). Caching disabled.", exc)
    redis_client = None


def cache_get(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning("Cache GET error for key '%s': %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as exc:
        logger.warning("Cache SET error for key '%s': %s", key, exc)


def cache_clear_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern. Returns number of keys deleted."""
    if not redis_client:
        return 0
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as exc:
        logger.warning("Cache CLEAR error for pattern '%s': %s", pattern, exc)
        return 0
