from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.models import Colleges
from database.db_connection import get_db, CandidateAllotment as CA, Colleges as CLG, Branch as B

router = APIRouter()


@router.post("/fetch_data")
def fetch_data(data: Colleges, db: Session = Depends(get_db)):
    query = db.query(
        CA.aggr_mark, CA.general_rank, CA.community_rank, CA.community,
        CA.college_code, CLG.college_name, B.branch_name,
        CA.allotted_category, CA.year, CA.round
    ).outerjoin(CLG, CA.college_code == CLG.college_code
    ).outerjoin(B, CA.branch_code == B.branch_code)

    if data.Group:
        query = query.filter(B.category.in_(data.Group))
    if data.Year:
        query = query.filter(CA.year.in_(data.Year))
    if data.Community:
        query = query.filter(CA.community.in_(data.Community))
    if data.Department:
        query = query.filter(CA.branch_code.in_(data.Department))
    if data.Region:
        query = query.filter(CLG.region.in_(data.Region))
    if data.District:
        query = query.filter(CLG.location.in_(data.District))

    if data.Cutoff:
        value = data.Cutoff[0]
        if value == "between":
            query = query.filter(CA.aggr_mark.between(data.FirstValue[0], data.SecondValue[0]))
        elif value == ">":
            query = query.filter(CA.aggr_mark > data.FirstValue[0])
        elif value == "<":
            query = query.filter(CA.aggr_mark < data.FirstValue[0])
        elif value == ">=":
            query = query.filter(CA.aggr_mark >= data.FirstValue[0])
        elif value == "<=":
            query = query.filter(CA.aggr_mark <= data.FirstValue[0])
        elif value == "=":
            query = query.filter(CA.aggr_mark == data.FirstValue[0])

    if data.CollegeType:
        query = query.filter(CLG.college_type.in_(data.CollegeType))

    results = query.order_by(CA.year.desc(), CA.aggr_mark.desc()).all()

    return [
        {
            "year": r.year,
            "aggr_mark": r.aggr_mark,
            "community": r.community,
            "college_code": r.college_code,
            "college_name": r.college_name,
            "branch_name": r.branch_name,
            "general_rank": r.general_rank,
            "community_rank": r.community_rank,
            "round": r.round,
            "allotted_category": r.allotted_category,
        }
        for r in results
    ]
