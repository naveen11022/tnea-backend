import os
import time
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

def create_engine_with_retry(url, max_retries=5, retry_delay=2):
    """Create engine with retry logic for database connection"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            # Test the connection
            engine.connect()
            print(f"✅ Database connected successfully")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Database connection attempt {attempt + 1} failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise e

engine = create_engine_with_retry(os.getenv("DATABASE_URL"))

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


@contextmanager
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_dep():
    with get_db() as db:
        yield db

class CandidateAllotment(Base):
    __tablename__ = 'candidate_allotment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    s_no = Column(Integer, nullable=True)
    aggr_mark = Column(Float)
    general_rank = Column(String(10))
    community_rank = Column(String(10))
    community = Column(String(50))
    college_code = Column(String(10))
    branch_code = Column(String(10))
    allotted_category = Column(String(50))
    year = Column(Integer)
    round = Column(String(10))


class Branch(Base):
    __tablename__ = 'branch'
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_code = Column(String(10), nullable=True)
    branch_name = Column(String(300), nullable=True)
    category = Column(String(50), nullable=True)


class Colleges(Base):
    __tablename__ = 'colleges'
    s_no = Column(Integer, nullable=True)
    college_code = Column(Integer, primary_key=True)
    college_name = Column(String(512), nullable=True)
    location = Column(String(512), nullable=True)
    region = Column(String(100), nullable=True)
    college_type = Column(String(100), nullable=True)


