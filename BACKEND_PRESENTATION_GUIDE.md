# 🎤 Backend Presentation Guide

If you are asked to explain the backend code (e.g., during an interview, project review, or presentation), **do not try to explain every single file**. 

Instead, focus on the **"Request Journey"** — tracing how data flows from the moment a user clicks "Check" to when the result is saved in the database.

Open and explain these **4 core files** in this exact order:

---

## 1. The Entry Point (API Routes)
**File to open:** `backend/app/api/prediction.py`

**What to explain:**
*   This is the REST API layer built with FastAPI.
*   Show the `POST /check-interaction` route. Explain that it receives the `drug_a` and `drug_b` JSON payload from the React frontend.
*   Show the `GET /history` route. Explain that it handles pagination and dynamic filtering (e.g., filtering by severity or date) so the user can view their past checks on the dashboard.
*   Mention that routes are protected by a JWT authentication dependency (`Depends(get_current_user)`).

---

## 2. The Business Logic
**File to open:** `backend/app/services/prediction_service.py`

**What to explain:**
*   Explain the **Service Layer Pattern**. The API route shouldn't have complex logic, so it hands the request to this service.
*   Walk through how this file orchestrates the workflow:
    1.  It asks the Machine Learning engine for a prediction.
    2.  It asks the Explainer Service for SHAP feature contributions.
    3.  It bundles the results together and saves them to the SQLite database.

---

## 3. The "Brain" (Machine Learning Inference)
**File to open:** `backend/app/ml/fusion_net.py`

> [!IMPORTANT]  
> *This is the most critical file to explain in a Machine Learning backend.*

**What to explain:**
*   Explain that this file implements the `SemanticFusionNet v3.0`.
*   Walk through the **3-Tier Cascade System**:
    *   **Tier 1 (Exact Match):** Show how it first looks up the pair in the `_pairs_lookup` dictionary for an instant response based on 75,537 historical FAERS reports.
    *   **Tier 2 (ML Ensemble):** If the pair is novel (never seen before), show how it extracts the 64-dim embeddings, builds a 133-dim feature vector, and runs the XGBoost + CatBoost soft-voting ensemble.
    *   **Tier 3 (Simulation):** Mention the deterministic fallback that guarantees 100% uptime even if model files are missing.

---

## 4. The Database & Validation
**Files to open:** `backend/app/db/models.py` & `backend/app/schemas/prediction.py`

**What to explain:**
*   Show `models.py` to explain how data is persisted using **SQLAlchemy ORM**. Highlight that you are storing critical audit data like `severity_label`, `confidence_score`, and `faers_reports`.
*   Show `schemas/prediction.py` to explain how you use **Pydantic** to validate incoming JSON requests and format outgoing responses, ensuring the API never crashes from bad data.

---

### 💡 The "Elevator Pitch" Summary

If they just ask for a 30-second summary of how the backend works, say:

> *"The backend is built with **FastAPI**. When the frontend requests a drug check, the API router passes it to a **Service Layer**. The Service Layer consults our **FusionNet ML Engine**, which uses a 3-tier cascade—checking a database of 75,000 known pairs first, and falling back to a Graph Attention Network and XGBoost ensemble for novel pairs. Finally, the service saves the risk assessment to a **SQLite** database via SQLAlchemy and returns the clinical report to the user."*
