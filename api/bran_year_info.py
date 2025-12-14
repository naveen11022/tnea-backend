from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db, Branch, CandidateAllotment

router = APIRouter()


@router.get('/get_branch', tags=['Branch'])
async def get_branch(db: Session = Depends(get_db)):
    try:
        branches = db.query(Branch.branch_code, Branch.branch_name).all()
        results = [[branch.branch_code, branch.branch_name] for branch in branches]
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get('/get_year', tags=['Year'])
async def get_year(db: Session = Depends(get_db)):
    try:
        years = db.query(CandidateAllotment.year).distinct().order_by(CandidateAllotment.year.desc()).all()
        results = [year[0] for year in years]
        return results
    except Exception as e:
        return {"error": str(e)}
