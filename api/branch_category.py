from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Branch
from caching.cache import redis_client
import json
router = APIRouter()


@router.get('/get_branch_category', tags=['Region'])
async def get_region(db: Session = Depends(get_db)):
    try:
        cache_key = "unique_branch"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        categories = db.query(Branch.category).distinct().all()
        result =  [category[0] for category in categories]
        redis_client.setex(cache_key,3600,json.dumps(result))
        return result
    

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
