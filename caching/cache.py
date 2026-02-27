import redis
import os

try:
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Test connection
        redis_client.ping()
        print("✅ Redis connected successfully")
    else:
        print("⚠️ REDIS_URL not set, caching disabled")
        redis_client = None
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}, caching disabled")
    redis_client = None
