from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
import math

class PredictionBase(BaseModel):
    drug_a: str
    drug_b: str
    indication: Optional[str] = None
    substance: Optional[str] = None

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    user_id: int
    severity_label: str
    confidence_score: float
    explanation: str
    recommendation: Optional[str] = None
    alternatives: List[str] = []
    risk_factors: List[str] = []
    risk_score: float = 0.0
    created_at: datetime

    @field_validator('alternatives', 'risk_factors', mode='before')
    @classmethod
    def parse_list_fields(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if not v: return []
            return [x.strip() for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return v
        return []

    model_config = ConfigDict(from_attributes=True)

class DashboardSummary(BaseModel):
    total_predictions: int
    major_severity_count: int
    moderate_severity_count: int
    minor_severity_count: int
    no_interaction_count: int
    recent_predictions: List[Prediction]

class PaginatedHistory(BaseModel):
    """
    Paginated wrapper returned by GET /api/v1/history.

    Fields
    ------
    items   : the prediction records for the current page
    total   : total number of records matching the current filter
    page    : current page number (1-indexed)
    limit   : records per page
    pages   : total number of pages
    """
    items: List[Prediction]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def build(cls, items: List[Prediction], total: int, page: int, limit: int) -> "PaginatedHistory":
        pages = math.ceil(total / limit) if limit > 0 else 1
        return cls(items=items, total=total, page=page, limit=limit, pages=pages)

