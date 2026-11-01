from app.db.database import SessionLocal, engine, Base
from app.db import models
from app.core.security import get_password_hash
from app.crud import user as user_crud
from app.schemas import user as user_schema

def seed_database():
    # Ensure tables exist before seeding
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if user already exists
        test_email = "admin@example.com"
        db_user = user_crud.get_user_by_email(db, email=test_email)
        
        if not db_user:
            print(f"Seeding test user: {test_email}")
            user_in = user_schema.UserCreate(
                name="Test Admin",
                email=test_email,
                password="password123"
            )
            user_crud.create_user(db, user_in)
            print("Database seeded successfully.")
        else:
            print("Test user already exists.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
