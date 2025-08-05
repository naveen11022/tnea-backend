from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Colleges, CandidateAllotment

router = APIRouter()


@router.get('/get_region', tags=['Region'])
async def get_region(db: Session = Depends(get_db)):
    try:
        regions = db.query(Colleges.region).distinct().all()
        return [region[0] for region in regions]
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}


@router.get('/get_category', tags=['Category'])
async def get_category(db: Session = Depends(get_db)):
    try:
        categories = db.query(CandidateAllotment.community).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
