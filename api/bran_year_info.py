from fastapi import APIRouter
from database.db_connection import session, Branch, CandidateAllotment

router = APIRouter()


@router.get('/get_branch', tags=['Branch'])
async def get_branch():
    try:
        branches = session.query(Branch.branch_code, Branch.branch_name).all()
        results = []
        for branch in branches:
            results.append([branch[0], branch[1]])
        return results
    except Exception as e:
        print(e)
        return {"error": str(e)}


@router.get('/get_year', tags=['Year'])
async def get_year():
    try:
        results = []
        years = session.query(CandidateAllotment.year).distinct().order_by(CandidateAllotment.year.desc()).all()
        for year in years:
            results.append(year[0])
        return results
    except Exception as e:
        print(e)
        return {"error": str(e)}
