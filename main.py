import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from database.db_connection import Base, engine
from rate_limit.rate_limiter import limiter

from api.district import router as district_router
from api.branch_category import router as branch_category_router
from api.bran_year_info import router as bran_year_info_router
from api.region_cate_info import router as region_cate_info_router
from api.fetch_data import router as fetch_data_router
from analytics.router import router as analytics_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CORS origins
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="TNEA Backend API",
    version="1.0.0",
    description="TNEA counselling data API",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(bran_year_info_router, prefix="/api")
app.include_router(region_cate_info_router, prefix="/api")
app.include_router(fetch_data_router, prefix="/api")
app.include_router(branch_category_router, prefix="/api")
app.include_router(district_router, prefix="/api")
app.include_router(analytics_router)


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"Hello": "Tnea Backend"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
