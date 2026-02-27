from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Request
from database.db_connection import get_db_dep, Branch, CandidateAllotment
from caching.cache import redis_client
# from rate_limit.rate_limiter import limiter
import json

router = APIRouter()


@router.get("/get_branch", tags=["Branch"])
# @limiter.limit("20/minute")
async def get_branch(request: Request, db: Session = Depends(get_db_dep)):
    try:
        cache_key = "branch"
        if redis_client:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                return json.loads(cache_data)
        branches = db.query(Branch.branch_code, Branch.branch_name).all()
        results = [[branch.branch_code, branch.branch_name] for branch in branches]
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get("/get_year", tags=["Year"])
# @limiter.limit("20/minute")
async def get_year(request: Request,db: Session = Depends(get_db_dep)):
    try:
        cache_key = "year"
        if redis_client:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                return json.loads(cache_data)
        years = db.query(CandidateAllotment.year).distinct().order_by(CandidateAllotment.year.desc()).all()
        results = [year[0] for year in years]
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        return results
    except Exception as e:
        return {"error": str(e)}
