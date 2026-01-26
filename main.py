from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

import uvicorn

from api.district import router as district_router
from api.branch_category import router as branch_category_router
from api.bran_year_info import router as get_db_details
from api.region_cate_info import router as region_cate_info
from api.fetch_data import router as fetch_data

from rate_limit.rate_limiter import limiter

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(get_db_details)
app.include_router(region_cate_info)
app.include_router(fetch_data)
app.include_router(branch_category_router)
app.include_router(district_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
