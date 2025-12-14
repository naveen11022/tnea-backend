from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Branch

router = APIRouter()


@router.get('/get_branch_category', tags=['Region'])
async def get_region(db: Session = Depends(get_db)):
    try:
        categories = db.query(Branch.category).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
