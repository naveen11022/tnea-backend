from fastapi import APIRouter
from database.db_connection import Colleges, Allotment

router = APIRouter()


@router.get("/get_region")
async def get_region():
    regions = Colleges.objects.distinct('region')
    return regions


@router.post("/get_category")
async def get_category():
    category = Allotment.objects.distinct('community')
    return category
