from upstash_redis import Redis
import os
from dotenv import load_dotenv
load_dotenv()
redis_client = Redis(url="https://vocal-vervet-20039.upstash.io",
                     token=os.getenv("CACHE_URL"))
