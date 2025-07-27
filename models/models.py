from pydantic import BaseModel
from typing import Optional, List


class Colleges(BaseModel):
    Year: Optional[List[int]] = []
    Community: Optional[List[str]] = []
    Region: Optional[List[str]] = []
    Department: Optional[List[str]] = []
    Cutoff: Optional[List[str]] = []
    FirstValue: Optional[List[float]] = []
    SecondValue: Optional[List[float]] = []
