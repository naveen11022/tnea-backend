from pydantic import BaseModel
from typing import List, Optional


class AnalyticsFilterRequest(BaseModel):
    years: Optional[List[int]] = []
    districts: Optional[List[str]] = []
    college_types: Optional[List[str]] = []
    branch_categories: Optional[List[str]] = []
    top_n: Optional[int] = 10
