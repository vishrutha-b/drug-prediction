from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from .base import BaseRepository
from ..db.models import Prediction
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException

# ---------------------------------------------------------------------------
# Field configuration
# ---------------------------------------------------------------------------

# Fields the user is allowed to filter on.
# Maps param name -> (ORM column, python type for value coercion)
ALLOWED_FILTER_FIELDS: Dict[str, Tuple[Any, type]] = {
    "drug_a":          (Prediction.drug_a,          str),
    "drug_b":          (Prediction.drug_b,          str),
    "indication":      (Prediction.indication,      str),
    "substance":       (Prediction.substance,       str),
    "severity_label":  (Prediction.severity_label,  str),
    "confidence_score":(Prediction.confidence_score, float),
    "risk_score":      (Prediction.risk_score,       float),
    "created_at":      (Prediction.created_at,       datetime),
}

# Fields the user is allowed to sort on.
ALLOWED_SORT_FIELDS: Dict[str, Any] = {
    "created_at":       Prediction.created_at,
    "risk_score":       Prediction.risk_score,
    "confidence_score": Prediction.confidence_score,
    "severity_label":   Prediction.severity_label,
}

# Operators that only make sense on numeric / date columns (not plain text).
RANGE_OPERATORS = {"gte", "lte", "gt", "lt"}


def _coerce(value: str, col_type: type):
    """Convert a raw query-string value to the expected Python type."""
    if col_type is float:
        try:
            return float(value)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Expected a number, got '{value}'")
    if col_type is datetime:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date/datetime '{value}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."
        )
    return value  # str — no coercion needed


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self):
        super().__init__(Prediction)

    # ------------------------------------------------------------------
    # Existing helpers (unchanged)
    # ------------------------------------------------------------------

    def create(self, db: Session, obj_in):
        # Serialize list fields to comma-separated strings for DB storage.
        for field in ["alternatives", "risk_factors"]:
            if field in obj_in and isinstance(obj_in[field], list):
                obj_in[field] = ", ".join(obj_in[field])
        return super().create(db, obj_in)

    def get_user_history(self, db: Session, user_id: int, limit: int = 50) -> List[Prediction]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_severity_counts(self, db: Session, user_id: int):
        from sqlalchemy import func
        return (
            db.query(self.model.severity_label, func.count(self.model.id))
            .filter(self.model.user_id == user_id)
            .group_by(self.model.severity_label)
            .all()
        )

    # ------------------------------------------------------------------
    # NEW: Dynamic filtering engine
    # ------------------------------------------------------------------

    def get_filtered_history(
        self,
        db: Session,
        user_id: Optional[int],          # None  → all records; int → one user's records
        raw_params: Dict[str, str],
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[Prediction], int]:
        """
        Build and execute a fully dynamic, safe filtering query.

        How the parameter parsing works
        --------------------------------
        Each key arriving from the query string is split on '__' to extract
        the field name and the optional operator:

            drug_a=Warfarin          → field='drug_a', op='eq',  value='Warfarin'
            risk_score__gte=70       → field='risk_score', op='gte', value='70'
            severity_label=A|B|C     → field='severity_label', op='in', values=['A','B','C']
            drug_a__contains=war     → field='drug_a', op='contains', value='war'

        Scope
        -----
        - Pass user_id=<int>  → filter only that user's records (personal history).
        - Pass user_id=None   → query ALL records in the table (global research view).
        - Range operators (__gte etc.) are rejected on plain-text columns.

        Returns
        -------
        (items, total_count) — the paginated list plus the total unfiltered count
        so the caller can build pagination metadata.
        """

        # 1. Validate sort field
        if sort_by not in ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field '{sort_by}'. Allowed: {list(ALLOWED_SORT_FIELDS)}"
            )
        if order not in ("asc", "desc"):
            raise HTTPException(
                status_code=400,
                detail="'order' must be 'asc' or 'desc'."
            )

        # 2. Start query — scope to a single user OR all records
        query = db.query(self.model)
        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)

        # 3. Parse and apply each filter parameter
        for raw_key, raw_value in raw_params.items():
            # Split 'field__operator' → ('field', 'operator')
            parts = raw_key.split("__", 1)
            field_name = parts[0]
            operator   = parts[1] if len(parts) == 2 else "eq"

            # 3a. Reject unknown fields immediately
            if field_name not in ALLOWED_FILTER_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Unknown or disallowed filter field: '{field_name}'. "
                        f"Allowed fields: {list(ALLOWED_FILTER_FIELDS)}"
                    )
                )

            col, col_type = ALLOWED_FILTER_FIELDS[field_name]

            # 3b. IN filter — triggered when value contains '|'
            #     Example: severity_label=DEATH RISK|HOSPITAL ADMISSION
            if "|" in raw_value and operator == "eq":
                values = [v.strip() for v in raw_value.split("|") if v.strip()]
                coerced = [_coerce(v, col_type) for v in values]
                query = query.filter(col.in_(coerced))
                continue

            # 3c. Range operators — only valid on numeric/date columns
            if operator in RANGE_OPERATORS:
                if col_type is str:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operator '__{operator}' is not supported for text field '{field_name}'."
                    )
                coerced_value = _coerce(raw_value, col_type)
                if operator == "gte":
                    query = query.filter(col >= coerced_value)
                elif operator == "lte":
                    query = query.filter(col <= coerced_value)
                elif operator == "gt":
                    query = query.filter(col > coerced_value)
                elif operator == "lt":
                    query = query.filter(col < coerced_value)
                continue

            # 3d. Case-insensitive LIKE — triggered by __contains
            if operator == "contains":
                if col_type is not str:
                    raise HTTPException(
                        status_code=400,
                        detail=f"'__contains' is only valid for text fields, not '{field_name}'."
                    )
                # SQLite ilike is not natively supported; use func.lower for portability
                query = query.filter(col.ilike(f"%{raw_value}%"))
                continue

            # 3e. Reject any other unknown operator
            if operator != "eq":
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Unknown operator '__{operator}'. "
                        "Supported: (none / eq), __gte, __lte, __gt, __lt, __contains."
                    )
                )

            # 3f. Exact match (default)
            coerced_value = _coerce(raw_value, col_type)
            query = query.filter(col == coerced_value)

        # 4. Get total count BEFORE pagination (for frontend pagination UI)
        total = query.count()

        # 5. Apply sorting
        sort_col = ALLOWED_SORT_FIELDS[sort_by]
        order_fn = desc if order == "desc" else asc
        query = query.order_by(order_fn(sort_col))

        # 6. Apply pagination
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        return items, total


prediction_repo = PredictionRepository()
