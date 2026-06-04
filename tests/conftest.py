"""
Shared fixtures for API tests.

Uses an in-memory SQLite database so tests run without a real MySQL/Redis instance.
The database module is patched before main.py is imported to avoid real DB connections.
"""
import os
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Force in-memory backends BEFORE any app module is imported
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ["RATE_LIMIT_STORAGE"] = "memory://"

# ---------------------------------------------------------------------------
# Patch DB engine creation BEFORE any app module is imported
# ---------------------------------------------------------------------------
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

_engine_patch = patch(
    "database.db_connection.create_engine_with_retry",
    return_value=test_engine,
)
_engine_patch.start()

# Now safe to import app modules
import caching.cache as cache_module  # noqa: E402
from database.db_connection import Base, get_db_dep  # noqa: E402


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
def _seed(db):
    from database.db_connection import CandidateAllotment, Branch, Colleges
    db.add_all([
        Branch(id=1, branch_code="CS", branch_name="Computer Science", category="Engineering"),
        Branch(id=2, branch_code="EC", branch_name="Electronics", category="Engineering"),
    ])
    db.add_all([
        Colleges(college_code=1001, college_name="ABC College", location="Chennai",
                 region="Chennai", college_type="Government"),
        Colleges(college_code=1002, college_name="XYZ College", location="Coimbatore",
                 region="Coimbatore", college_type="Private"),
    ])
    db.add_all([
        CandidateAllotment(
            id=1, s_no=1, aggr_mark=195.5, general_rank="100", community_rank="50",
            community="OC", college_code="1001", branch_code="CS",
            allotted_category="OC", year=2023, round="1",
        ),
        CandidateAllotment(
            id=2, s_no=2, aggr_mark=180.0, general_rank="200", community_rank="80",
            community="BC", college_code="1002", branch_code="EC",
            allotted_category="BC", year=2022, round="2",
        ),
    ])
    db.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    _seed(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def client(setup_db):
    # Disable Redis for tests
    cache_module.redis_client = None

    from main import app
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db_dep] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()
