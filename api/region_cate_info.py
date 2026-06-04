import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Colleges, CandidateAllotment
from caching.cache import cache_get, cache_set
from rate_limit.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/get_region", tags=["Region"])
@limiter.limit("20/minute")
async def get_region(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("region")
    if cached is not None:
        return cached

    try:
        rows = db.query(Colleges.region).distinct().all()
        result = sorted([r[0] for r in rows if r[0] is not None])
        cache_set("region", result)
        return result
    except Exception as exc:
        logger.exception("Error in get_region")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/get_category", tags=["Category"])
@limiter.limit("20/minute")
async def get_category(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("category")
    if cached is not None:
        return cached

    try:
        rows = db.query(CandidateAllotment.community).distinct().all()
        result = sorted([r[0] for r in rows if r[0] is not None])
        cache_set("category", result)
        return result
    except Exception as exc:
        logger.exception("Error in get_category")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
