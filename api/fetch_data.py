import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import cast, Integer
from models.models import Colleges as CollegesSchema
from database.db_connection import (
    get_db_dep,
    CandidateAllotment as CA,
    Colleges as CLG,
    Branch as B,
)
from rate_limit.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

CUTOFF_OPS = {
    ">": lambda col, v: col > v,
    "<": lambda col, v: col < v,
    ">=": lambda col, v: col >= v,
    "<=": lambda col, v: col <= v,
    "=": lambda col, v: col == v,
}


@router.post("/fetch_data", tags=["Data"])
@limiter.limit("30/minute")
def fetch_data(request: Request, data: CollegesSchema, db: Session = Depends(get_db_dep)):
    try:
        query = db.query(
            CA.aggr_mark, CA.general_rank, CA.community_rank, CA.community,
            CA.college_code, CLG.college_name, B.branch_name,
            CA.allotted_category, CA.year, CA.round,
        ).outerjoin(
            CLG, cast(CA.college_code, Integer) == CLG.college_code
        ).outerjoin(
            B, CA.branch_code == B.branch_code
        )

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
        if data.CollegeType:
            query = query.filter(CLG.college_type.in_(data.CollegeType))

        if data.Cutoff:
            op = data.Cutoff[0]
            if op == "between" and data.FirstValue and data.SecondValue:
                query = query.filter(CA.aggr_mark.between(data.FirstValue[0], data.SecondValue[0]))
            elif op in CUTOFF_OPS and data.FirstValue:
                query = query.filter(CUTOFF_OPS[op](CA.aggr_mark, data.FirstValue[0]))

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

    except Exception as exc:
        logger.exception("Error in fetch_data")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
