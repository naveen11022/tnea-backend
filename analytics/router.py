import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db_connection import get_db_dep
from rate_limit.rate_limiter import limiter
from caching.cache import cache_get, cache_set
from analytics.schemas import AnalyticsFilterRequest
from analytics import queries
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def make_cache_key(prefix: str, obj) -> str:
    return f"analytics:{prefix}:{json.dumps(obj, sort_keys=True, default=str)}"


@router.get("/districts")
@limiter.limit("30/minute")
async def get_all_districts(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("analytics:districts")
    if cached is not None:
        return cached
    try:
        data = queries.get_all_districts(db)
        cache_set("analytics:districts", data, ttl=3600)
        return data
    except Exception as exc:
        logger.exception("Error in get_all_districts")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/branch-trends")
@limiter.limit("30/minute")
async def branch_trends(request: Request, filters: AnalyticsFilterRequest, db: Session = Depends(get_db_dep)):
    key = make_cache_key("branch-trends", filters.model_dump())
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        data = queries.get_branch_trends(
            db, filters.years, filters.districts,
            filters.college_types, filters.branch_categories, filters.top_n or 10
        )
        cache_set(key, data, ttl=600)
        return data
    except Exception as exc:
        logger.exception("Error in branch_trends")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/top-district-branches")
@limiter.limit("30/minute")
async def top_district_branches(request: Request, filters: AnalyticsFilterRequest, db: Session = Depends(get_db_dep)):
    key = make_cache_key("top-district-branches", filters.model_dump())
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        data = queries.get_top_district_branches(
            db, filters.years, filters.districts,
            filters.college_types, filters.branch_categories, filters.top_n or 10
        )
        cache_set(key, data, ttl=600)
        return data
    except Exception as exc:
        logger.exception("Error in top_district_branches")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/top-year-branches")
@limiter.limit("30/minute")
async def top_year_branches(request: Request, filters: AnalyticsFilterRequest, db: Session = Depends(get_db_dep)):
    key = make_cache_key("top-year-branches", filters.model_dump())
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        data = queries.get_top_year_branches(
            db, filters.years, filters.districts,
            filters.college_types, filters.branch_categories, filters.top_n or 10
        )
        cache_set(key, data, ttl=600)
        return data
    except Exception as exc:
        logger.exception("Error in top_year_branches")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/top-college-branches")
@limiter.limit("30/minute")
async def top_college_branches(request: Request, filters: AnalyticsFilterRequest, db: Session = Depends(get_db_dep)):
    key = make_cache_key("top-college-branches", filters.model_dump())
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        data = queries.get_top_college_branches(
            db, filters.years, filters.districts,
            filters.college_types, filters.branch_categories, filters.top_n or 5
        )
        cache_set(key, data, ttl=600)
        return data
    except Exception as exc:
        logger.exception("Error in top_college_branches")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/dashboard-summary")
@limiter.limit("30/minute")
async def dashboard_summary(request: Request, db: Session = Depends(get_db_dep)):
    cached = cache_get("analytics:dashboard-summary")
    if cached is not None:
        return cached
    try:
        data = queries.get_dashboard_summary(db)
        cache_set("analytics:dashboard-summary", data, ttl=600)
        return data
    except Exception as exc:
        logger.exception("Error in dashboard_summary")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
