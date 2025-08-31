from database.db_connection import Branch, Allotment

from fastapi import APIRouter

router = APIRouter()


@router.get("/get_branch")
async def get_branch():
    branches = Branch.objects.all()
    branch_list = []
    for branch in branches:
        branch_list.append([branch.branch_code, branch.branch_name])

    return branch_list


@router.get("/get_year")
async def get_year():
    years = Allotment.objects.distinct('year')
    return years

