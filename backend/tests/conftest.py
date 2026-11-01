"""
conftest.py — shared fixtures for the backend test suite.

Uses a single persistent SQLite in-memory connection (StaticPool) so that
create_all() and every subsequent session all share the same DB state.
All tests are isolated from the real file-based database.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models BEFORE Base.metadata so all tables are registered.
import app.db.models as _models  # noqa: F401
from app.db.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# StaticPool: every call to engine.connect() returns the SAME underlying
# sqlite3 connection, so create_all() and all request sessions share one DB.
# ---------------------------------------------------------------------------
test_engine = create_engine(
    "sqlite://",                          # in-memory
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

# Create schema once on the shared connection.
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the override for the entire test process.
app.dependency_overrides[get_db] = override_get_db

