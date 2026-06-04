import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep, Branch
from caching.cache import cache_get, cache_set
from rate_limit.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

CACHE_KEY = "unique_branch"


@router.get("/get_branch_category", tags=["Region"])
@limiter.limit("20/minute")
async def get_branch_category(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get(CACHE_KEY)
    if cached is not None:
        return cached

    try:
        categories = db.query(Branch.category).distinct().all()
        result = [row[0] for row in categories if row[0] is not None]
        cache_set(CACHE_KEY, result)
        return result
    except Exception as exc:
        logger.exception("Error in get_branch_category")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
