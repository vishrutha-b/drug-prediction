from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..core.config import settings

# For SQLite, we need to allow multithreading access
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
