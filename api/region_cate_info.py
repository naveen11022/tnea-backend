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
            try:
                cache_data = redis_client.get(cache_key)
                if cache_data:
                    return json.loads(cache_data)
            except Exception as cache_error:
                print(f"Cache error: {cache_error}")
        
        regions = db.query(Colleges.region).distinct().all()
        result = [region[0] for region in regions if region[0] is not None]
        result.sort()
        
        if redis_client:
            try:
                redis_client.setex(cache_key, 3600, json.dumps(result))
            except Exception as cache_error:
                print(f"Cache set error: {cache_error}")
        
        return result
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@router.get("/get_category", tags=["Category"])
# @limiter.limit("20/minute")
async def get_category(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "category"
        if redis_client:
            try:
                cache_data = redis_client.get(cache_key)
                if cache_data:
                    return json.loads(cache_data)
            except Exception as cache_error:
                print(f"Cache error: {cache_error}")
        
        categories = db.query(CandidateAllotment.community).distinct().all()
        result = [category[0] for category in categories if category[0] is not None]
        result.sort()
        
        if redis_client:
            try:
                redis_client.setex(cache_key, 3600, json.dumps(result))
            except Exception as cache_error:
                print(f"Cache set error: {cache_error}")
        
        return result
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
