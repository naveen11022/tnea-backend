from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database.db_connection import Colleges, get_db_dep
from models.models import Regions
from caching.cache import redis_client
# from rate_limit.rate_limiter import limiter
import json

router = APIRouter()


@router.post("/districts")
# @limiter.limit("15/minute")
def get_districts(request: Request, district: Regions, db: Session = Depends(get_db_dep)):
    try:
        districts_query = (
            db.query(Colleges.location)
            .filter(Colleges.region.in_(district.District))
            .distinct()
            .all()
        )
        results = [loc[0] for loc in districts_query]
        results.sort()
        return results
    except Exception as e:
        print("Error fetching districts:", e)
        return []


@router.get("/college_type")
# @limiter.limit("20/minute")
def get_college(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "college_type"
        if redis_client:
            try:
                cache_data = redis_client.get(cache_key)
                if cache_data:
                    return json.loads(cache_data)
            except Exception as cache_error:
                print(f"Cache error: {cache_error}")
        
        college_type = db.query(Colleges.college_type).distinct().all()
        result = [college[0] for college in college_type if college[0] is not None]
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
