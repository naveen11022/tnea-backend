from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import Colleges, get_db
from models.models import Regions
from caching.cache import redis_client
import json

router = APIRouter()


@router.post('/districts')
def get_districts(district: Regions, db: Session = Depends(get_db)):
    try:
        cache_key = "districts"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        districts_query = (
            db.query(Colleges.location)
            .filter(Colleges.region.in_(district.District))
            .distinct()
            .all()
        )
        results = [loc[0] for loc in districts_query]
        results.sort()
        redis_client.setex(cache_key,3600,json.dumps(results))
        return results

    except Exception as e:
        print("Error fetching districts:", e)


@router.get("/college_type")
def get_college(db:Session=Depends(get_db)):
    try:
        cache_key = "college_type"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        college_type = db.query(Colleges.college_type).distinct().all()
        result =  [college[0] for college in college_type]
        redis_client.setex(cache_key,3600,json.dumps(result))
        return result
    
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
