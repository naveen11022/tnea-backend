from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Colleges, CandidateAllotment
from caching.cache import redis_client
# from rate_limit.rate_limiter import limiter
import json

router = APIRouter()


@router.get("/get_region", tags=["Region"])
# @limiter.limit("20/minute")
async def get_region(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "region"
        if redis_client:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                return json.loads(cache_data)
        regions = db.query(Colleges.region).distinct().all()
        result = [region[0] for region in regions]
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(result))
        return result
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}


@router.get("/get_category", tags=["Category"])
# @limiter.limit("20/minute")
async def get_category(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "category"
        if redis_client:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                return json.loads(cache_data)
        categories = db.query(CandidateAllotment.community).distinct().all()
        result = [category[0] for category in categories]
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(result))
        return result
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
