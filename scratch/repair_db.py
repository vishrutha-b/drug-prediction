import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from app.db.database import engine, Base
from app.db import models
from sqlalchemy import inspect

print(f"Targeting Database URL: {engine.url}")

# 1. Force table creation
print("Ensuring tables are created...")
Base.metadata.create_all(bind=engine)

# 2. Inspect columns
inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('predictions')]
print(f"Columns found in 'predictions' table: {columns}")

if 'risk_score' in columns:
    print("SUCCESS: risk_score column detected!")
else:
    print("FAILURE: risk_score column is still missing!")
