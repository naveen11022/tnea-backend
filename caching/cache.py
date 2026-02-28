import os
import redis

redis_url = os.getenv("REDIS_URL")

try:
    redis_client= redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    print("✅ Connected to Upstash Redis")
except Exception as e:
    print("❌ Redis connection error:", e)
