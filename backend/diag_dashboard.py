from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.repositories.prediction_repository import prediction_repo
from app.db import models

# Force schema sync
Base.metadata.create_all(bind=engine)

def diag_dashboard():
    db = SessionLocal()
    try:
        # Simulate a typical analytics request
        user = db.query(models.User).first()
        if not user:
            print("No test user found, creating mock professional...")
            user = models.User(name="Diag", email="diag@test.com", hashed_password="...")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        print(f"Aggregating data for User ID: {user.id}")
        predictions = prediction_repo.get_user_history(db, user.id)
        print(f"Found {len(predictions)} predictions.")
        
        summary = {
            "total_predictions": len(predictions),
            "major_severity_count": sum(1 for p in predictions if p.severity_label == "Major"),
            "recent_predictions": predictions[:5]
        }
        print("Summary aggregation successful.")
        return True
    except Exception as e:
        import traceback
        print("CRITICAL ERROR DETECTED:")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    diag_dashboard()
