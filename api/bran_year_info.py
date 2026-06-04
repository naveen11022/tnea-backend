import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Branch, CandidateAllotment
from caching.cache import cache_get, cache_set
from rate_limit.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/get_branch", tags=["Branch"])
@limiter.limit("20/minute")
async def get_branch(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("branch")
    if cached is not None:
        return cached

    try:
        branches = db.query(Branch.branch_code, Branch.branch_name).all()
        result = [[b.branch_code, b.branch_name] for b in branches]
        cache_set("branch", result)
        return result
    except Exception as exc:
        logger.exception("Error in get_branch")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/get_year", tags=["Year"])
@limiter.limit("20/minute")
async def get_year(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("year")
    if cached is not None:
        return cached

    try:
        years = (
            db.query(CandidateAllotment.year)
            .distinct()
            .order_by(CandidateAllotment.year.desc())
            .all()
        )
        result = [row[0] for row in years]
        cache_set("year", result)
        return result
    except Exception as exc:
        logger.exception("Error in get_year")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
