import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Colleges
from models.models import Regions
from caching.cache import cache_get, cache_set
from rate_limit.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/districts", tags=["District"])
@limiter.limit("15/minute")
def get_districts(request: Request, district: Regions, db: Session = Depends(get_db_dep)):
    try:
        rows = (
            db.query(Colleges.location)
            .filter(Colleges.region.in_(district.District))
            .distinct()
            .all()
        )
        return sorted([loc[0] for loc in rows if loc[0] is not None])
    except Exception as exc:
        logger.exception("Error in get_districts")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/college_type", tags=["College"])
@limiter.limit("20/minute")
def get_college_type(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("college_type")
    if cached is not None:
        return cached

    try:
        rows = db.query(Colleges.college_type).distinct().all()
        result = sorted([r[0] for r in rows if r[0] is not None])
        cache_set("college_type", result)
        return result
    except Exception as exc:
        logger.exception("Error in get_college_type")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
