from fastapi import APIRouter, Depends
from database.db_connection import Allotment, Branch, Colleges
router = APIRouter()