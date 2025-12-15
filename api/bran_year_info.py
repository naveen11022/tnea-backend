from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Branch, CandidateAllotment
from caching.cache import redis_client
import json
router = APIRouter()


@router.get('/get_branch', tags=['Branch'])
async def get_branch(db: Session = Depends(get_db)):
    try:
        cache_key = "branch"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        branches = db.query(Branch.branch_code, Branch.branch_name).all()
        results = [[branch.branch_code, branch.branch_name] for branch in branches]
        redis_client.setex(cache_key,3600,json.dumps(results))
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get('/get_year', tags=['Year'])
async def get_year(db: Session = Depends(get_db)):
    try:
        cache_key = "year"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        years = db.query(CandidateAllotment.year).distinct().order_by(CandidateAllotment.year.desc()).all()
        results = [year[0] for year in years]
        redis_client.setex(cache_key,3600,json.dumps(results))
        return results
    except Exception as e:
        return {"error": str(e)}
