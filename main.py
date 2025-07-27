from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from api.bran_year_info import router as get_db_details
from api.region_cate_info import router as region_cate_info
from api.fetch_data import router as fetch_data
app = FastAPI()

app.include_router(get_db_details)
app.include_router(region_cate_info)
app.include_router(fetch_data)

app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
