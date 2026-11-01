from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.database import get_db
from ..schemas import prediction as schemas
from ..services.prediction_service import prediction_service
from ..repositories.prediction_repository import prediction_repo
from .deps import get_current_user
from ..db import models

router = APIRouter(tags=["predict"])

# ---------------------------------------------------------------------------
# Reserved query-parameter names that must NOT be forwarded to the filter
# engine (they are handled explicitly by the route function).
# ---------------------------------------------------------------------------
_RESERVED_PARAMS = {"page", "limit", "sort_by", "order"}


@router.post("/check-interaction", response_model=schemas.Prediction)
def check_interaction(
    req: schemas.PredictionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Core Intelligence Endpoint: Runs SemanticFusionNet and generates clinical report.
    """
    # Delegate the actual prediction logic to the service layer.
    # We pass the database session, the request payload (req), and the ID of the user making the request.
    return prediction_service.process_prediction(db, req, current_user.id)


@router.get("/history", response_model=schemas.PaginatedHistory)
def get_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # --- Pagination ---
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=100, description="Results per page (max 100)"),
    # --- Sorting ---
    sort_by: str = Query(
        default="created_at",
        description="Sort field. Allowed: created_at, risk_score, confidence_score, severity_label"
    ),
    order: str = Query(
        default="desc",
        description="Sort direction: 'asc' or 'desc'"
    ),
    # --- Documented filter examples shown in Swagger ---
    drug_a: Optional[str] = Query(default=None, description="Exact match on drug_a (e.g. Warfarin)"),
    drug_b: Optional[str] = Query(default=None, description="Exact match on drug_b (e.g. Aspirin)"),
    severity_label: Optional[str] = Query(
        default=None,
        description="Exact match OR pipe-separated IN filter (e.g. 'DEATH RISK|HOSPITAL ADMISSION')"
    ),
    indication: Optional[str] = Query(default=None, description="Exact match on indication"),
    substance: Optional[str] = Query(default=None, description="Exact match on substance"),
    confidence_score__gte: Optional[float] = Query(default=None, description="confidence_score >= value"),
    confidence_score__lte: Optional[float] = Query(default=None, description="confidence_score <= value"),
    risk_score__gte: Optional[float] = Query(default=None, description="risk_score >= value"),
    risk_score__lte: Optional[float] = Query(default=None, description="risk_score <= value"),
    risk_score__gt: Optional[float] = Query(default=None, description="risk_score > value"),
    risk_score__lt: Optional[float] = Query(default=None, description="risk_score < value"),
    created_at__gte: Optional[str] = Query(
        default=None, description="created_at >= date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    ),
    created_at__lte: Optional[str] = Query(
        default=None, description="created_at <= date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    ),
    drug_a__contains: Optional[str] = Query(
        default=None, description="Case-insensitive substring match on drug_a"
    ),
    drug_b__contains: Optional[str] = Query(
        default=None, description="Case-insensitive substring match on drug_b"
    ),
):
    """
    Retrieves the authenticated user's prediction history with dynamic filtering,
    pagination, and sorting.

    ## Filtering

    Pass any combination of the query parameters documented below.
    All filters are AND-ed together.

    ### Operators
    | Syntax                  | Meaning                           |
    |-------------------------|-----------------------------------|
    | `field=value`           | Exact match                       |
    | `field=A\|B\|C`         | IN filter (pipe-separated)        |
    | `field__contains=value` | Case-insensitive substring search |
    | `field__gte=value`      | Greater than or equal             |
    | `field__lte=value`      | Less than or equal                |
    | `field__gt=value`       | Strictly greater than             |
    | `field__lt=value`       | Strictly less than                |

    ### Allowed filter fields
    `drug_a`, `drug_b`, `indication`, `substance`, `severity_label`,
    `confidence_score`, `risk_score`, `created_at`

    Unknown fields → **400 Bad Request**.
    """
    # Collect ALL raw query params from the request.
    # We strip out reserved parameters (like pagination/sorting) so the database filter engine
    # only receives the actual field filter keys (like drug_a, severity_label, etc.)
    raw_filters = {
        k: v
        for k, v in request.query_params.items()
        if k not in _RESERVED_PARAMS
    }

    # Pass the filters, pagination, and sorting instructions to the repository layer
    # which will construct and execute the final SQLAlchemy query.
    items, total = prediction_repo.get_filtered_history(
        db=db,
        user_id=current_user.id,
        raw_params=raw_filters,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
    )

    # Wrap the returned items and total count into a standardized pagination schema response
    return schemas.PaginatedHistory.build(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )



@router.get("/history/all", response_model=schemas.PaginatedHistory)
def get_all_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # --- Pagination ---
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=100, description="Results per page (max 100)"),
    # --- Sorting ---
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    # --- Filters ---
    drug_a: Optional[str] = Query(default=None),
    drug_b: Optional[str] = Query(default=None),
    severity_label: Optional[str] = Query(default=None),
    indication: Optional[str] = Query(default=None),
    substance: Optional[str] = Query(default=None),
    confidence_score__gte: Optional[float] = Query(default=None),
    confidence_score__lte: Optional[float] = Query(default=None),
    risk_score__gte: Optional[float] = Query(default=None),
    risk_score__lte: Optional[float] = Query(default=None),
    risk_score__gt: Optional[float] = Query(default=None),
    risk_score__lt: Optional[float] = Query(default=None),
    created_at__gte: Optional[str] = Query(default=None),
    created_at__lte: Optional[str] = Query(default=None),
    drug_a__contains: Optional[str] = Query(default=None),
    drug_b__contains: Optional[str] = Query(default=None),
):
    """
    Returns ALL predictions in the database (all users) with dynamic filtering,
    pagination, and sorting. Authentication is required.
    Same filter operators as GET /history.
    """
    raw_filters = {
        k: v
        for k, v in request.query_params.items()
        if k not in _RESERVED_PARAMS
    }

    items, total = prediction_repo.get_filtered_history(
        db=db,
        user_id=None,          # ← no user scope → all records
        raw_params=raw_filters,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
    )

    return schemas.PaginatedHistory.build(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{id}", response_model=schemas.Prediction)
def get_prediction_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets detailed report for a specific prediction ID."""
    prediction = prediction_repo.get_by_id(db, id)
    if not prediction or prediction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prediction report not found")
    return prediction
