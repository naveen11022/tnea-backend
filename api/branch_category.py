from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Branch
from fastapi import Request
from caching.cache import redis_client
# from rate_limit.rate_limiter import limiter
import json

router = APIRouter()


@router.get("/get_branch_category", tags=["Region"])
# @limiter.limit("20/minute")
async def get_region(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "unique_branch"
        if redis_client:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                return json.loads(cache_data)
        categories = db.query(Branch.category).distinct().all()
        result = [category[0] for category in categories]
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(result))
        return result
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
