from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import Colleges, get_db
from models.models import Regions

router = APIRouter()


@router.post('/districts')
def get_districts(district: Regions, db: Session = Depends(get_db)):
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
def get_college(db:Session=Depends(get_db)):
    try:
        college_type = db.query(Colleges.college_type).distinct().all()
        return [college[0] for college in college_type]
    
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
