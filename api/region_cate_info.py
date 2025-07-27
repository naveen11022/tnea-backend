from fastapi import APIRouter
from database.db_connection import session, Colleges, CandidateAllotment

router = APIRouter()


@router.get('/get_region', tags=['Region'])
async def get_region():
    try:
        regions = session.query(Colleges.region).distinct().all()
        results = []
        for region in regions:
            results.append(region[0])
        return results
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}


@router.get('/get_category', tags=['Category'])
async def get_category():
    try:
        categories = session.query(CandidateAllotment.community).distinct().all()
        result = []
        for category in categories:
            result.append(category[0])
        return result
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
