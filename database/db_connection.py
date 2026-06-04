import os
import time
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))


def create_engine_with_retry(url: str, max_retries: int = 5, retry_delay: int = 2):
    for attempt in range(max_retries):
        try:
            eng = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                pool_pre_ping=True,
                pool_recycle=1800,
            )
            with eng.connect():
                pass
            logger.info("Database connected successfully")
            return eng
        except Exception as exc:
            if attempt < max_retries - 1:
                logger.warning(
                    "DB connection attempt %d/%d failed: %s. Retrying in %ds...",
                    attempt + 1, max_retries, exc, retry_delay,
                )
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after %d attempts", max_retries)
                raise


engine = create_engine_with_retry(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class CandidateAllotment(Base):
    __tablename__ = "candidate_allotment"

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
    __tablename__ = "branch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_code = Column(String(10), nullable=True)
    branch_name = Column(String(300), nullable=True)
    category = Column(String(50), nullable=True)


class Colleges(Base):
    __tablename__ = "colleges"

    s_no = Column(Integer, nullable=True)
    college_code = Column(Integer, primary_key=True)
    college_name = Column(String(512), nullable=True)
    location = Column(String(512), nullable=True)
    region = Column(String(100), nullable=True)
    college_type = Column(String(100), nullable=True)
