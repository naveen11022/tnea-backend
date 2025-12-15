from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Colleges, CandidateAllotment
from caching.cache import redis_client
import json
router = APIRouter()


@router.get('/get_region', tags=['Region'])
async def get_region(db: Session = Depends(get_db)):
    try:
        cache_key = "region"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        regions = db.query(Colleges.region).distinct().all()
        result =  [region[0] for region in regions]
        redis_client.setex(cache_key,3600,json.dumps(result))
        return result
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}


@router.get('/get_category', tags=['Category'])
async def get_category(db: Session = Depends(get_db)):
    try:
        cache_key = "category"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        categories = db.query(CandidateAllotment.community).distinct().all()
        result =  [category[0] for category in categories]
        redis_client.setex(cache_key,3600,json.dumps(result))
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

