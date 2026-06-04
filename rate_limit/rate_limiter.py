import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE") or os.getenv("REDIS_URL", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATE_LIMIT_STORAGE,
    default_limits=["200/minute"],
)
