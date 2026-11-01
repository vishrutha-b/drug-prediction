from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..schemas import prediction as prediction_schema
from ..repositories.prediction_repository import prediction_repo
from .deps import get_current_user
from ..db import models

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=prediction_schema.DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Professional Data Aggregation via Repository
    predictions = prediction_repo.get_user_history(db, current_user.id)
    
    summary = {
        "total_predictions": len(predictions),
        "major_severity_count": sum(1 for p in predictions if p.severity_label == "Major"),
        "moderate_severity_count": sum(1 for p in predictions if p.severity_label == "Moderate"),
        "minor_severity_count": sum(1 for p in predictions if p.severity_label == "Minor"),
        "no_interaction_count": sum(1 for p in predictions if p.severity_label == "None"),
        "recent_predictions": predictions[:5]
    }
    return summary
