from sqlalchemy.orm import Session
from ..db import models
from ..schemas import prediction as prediction_schema
from typing import List

def create_prediction(db: Session, prediction_data: dict, user_id: int):
    # Professional serialization: Convert alternatives list to comma-separated string for DB storage
    if "alternatives" in prediction_data and isinstance(prediction_data["alternatives"], list):
        prediction_data["alternatives"] = ", ".join(prediction_data["alternatives"])
        
    db_prediction = models.Prediction(
        **prediction_data,
        user_id=user_id
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_user_predictions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Prediction).filter(
        models.Prediction.user_id == user_id
    ).order_by(models.Prediction.created_at.desc()).offset(skip).limit(limit).all()

def get_prediction(db: Session, prediction_id: int, user_id: int):
    return db.query(models.Prediction).filter(
        models.Prediction.id == prediction_id,
        models.Prediction.user_id == user_id
    ).first()

def get_dashboard_summary(db: Session, user_id: int):
    predictions = db.query(models.Prediction).filter(models.Prediction.user_id == user_id).all()
    
    summary = {
        "total_predictions": len(predictions),
        "major_severity_count": sum(1 for p in predictions if p.severity_label == "Major"),
        "moderate_severity_count": sum(1 for p in predictions if p.severity_label == "Moderate"),
        "minor_severity_count": sum(1 for p in predictions if p.severity_label == "Minor"),
        "no_interaction_count": sum(1 for p in predictions if p.severity_label == "None"),
        "recent_predictions": sorted(predictions, key=lambda x: x.created_at, reverse=True)[:5]
    }
    return summary
