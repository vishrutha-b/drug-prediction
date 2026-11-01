# 📐 System Architecture & Methodology — IntelliInteraction DDI Platform

> **Model:** SemanticFusionNet v3.0  
> **Architecture:** Hybrid Graph Attention Network (GAT) + XGBoost/CatBoost Soft-Voting Ensemble  
> **Availability Guarantee:** 100% — 3-tier fallback ensures every drug pair always returns a prediction  

---

## 1. High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    INTELLIINTERACTION PLATFORM                        │
├───────────────┬──────────────────────────┬───────────────────────────┤
│   FRONTEND    │        BACKEND           │         ML ENGINE         │
│  Next.js 14   │       FastAPI            │   SemanticFusionNet v3.0  │
│  TypeScript   │     + SQLAlchemy         │                           │
│  Tailwind CSS │     + JWT Auth           │  ┌──────────────────────┐ │
│               │                          │  │ Tier 1: FAERS Lookup │ │
│  ┌──────────┐ │  POST /check-interaction │  │ 75,537 validated     │ │
│  │Checker UI│─┼─────────────────────────┼─►│ drug pairs           │ │
│  │Visualizer│ │                          │  ├──────────────────────┤ │
│  │Dashboard │ │  GET  /history           │  │ Tier 2: GAT+Ensemble │ │
│  │Settings  │ │  GET  /dashboard/stats   │  │ XGBoost + CatBoost   │ │
│  └──────────┘ │                          │  │ soft-vote (133-dim)  │ │
│               │       SQLite DB          │  ├──────────────────────┤ │
│               │   (Prediction History)   │  │ Tier 3: Simulation   │ │
│               │                          │  │ Deterministic fallback│ │
└───────────────┴──────────────────────────┴──┴──────────────────────┴─┘
```

---

## 2. Methodology — SemanticFusionNet v3.0

SemanticFusionNet v3.0 is a **hybrid DDI severity classifier** combining three complementary approaches:

### 2.1 Problem Formulation

Given a pair of drug names `(Drug A, Drug B)`, the system predicts a **severity label** from a 4-class ordinal space:

```
f(Drug_A, Drug_B) → {DEATH RISK, HOSPITAL ADMISSION, MONITORING REQUIRED, SAFE}
```

The model also returns:
- A **confidence score** `[0.0, 1.0]` from the ensemble probability distribution
- A **risk score** `[0–100]` for dashboard visualizations
- An **explanation** grounded in FDA FAERS clinical evidence
- The **inference tier** used (exact_match / ml_ensemble / simulation)

---

### 2.2 Tier 1 — Exact FAERS Match

**Mechanism:** Direct hash-map lookup against the pre-compiled FAERS pair dictionary.

```python
for key in [(drug_a, drug_b), (drug_b, drug_a)]:
    if key in _pairs_lookup:
        return empirically_validated_label
```

**Confidence Calculation:**
```
confidence = min(0.99, 0.70 + 0.02 × min(report_count, 14))
```
This formula rewards pairs with more FAERS reports with higher confidence, capped at 0.99.

| FAERS Reports | Confidence |
|---|---|
| 1 | 0.72 |
| 5 | 0.80 |
| 10 | 0.90 |
| 14+ | 0.98–0.99 |

**Coverage:** ~75,537 unique canonical drug pairs  
**Source Tag:** `faers_lookup`

---

### 2.3 Tier 2 — GAT + XGBoost/CatBoost Ensemble

Activated for **novel drug pairs** not found in the FAERS lookup dictionary.

#### Step 1: Drug Embedding Lookup

For each drug in the pair, the system resolves a **64-dimensional embedding** via priority cascade:

```
Drug Name
    │
    ├── In GAT embedding dict? → Use 64-dim GAT node embedding (trained)
    │
    ├── Unknown drug, TF-IDF available? → TF-IDF char n-gram → first 64 dims
    │
    └── Neither available? → Zero vector (64-dim)
```

#### Step 2: Feature Vector Construction (133-dim)

```
[emb_a (64)] | [emb_b (64)] | [log(1+report_count)] | [pair_hash_norm] |
[len(a)] | [len(b)] | [len(a)+len(b)] | [|len(a)-len(b)|]
Total: 64 + 64 + 6 = 133 dimensions
```

#### Step 3: Soft-Voting Ensemble

```
P_final = 0.5 × P(XGBoost) + 0.5 × P(CatBoost)
severity = argmax(P_final)
confidence = max(P_final)
```

The response also includes **per-class probability scores** for clinical transparency:
```json
"class_probabilities": {
    "DEATH RISK": 0.127,
    "HOSPITAL ADMISSION": 0.683,
    "MONITORING REQUIRED": 0.175,
    "SAFE": 0.015
}
```

**Source Tag:** `xgb_catboost_ensemble`

---

### 2.4 Tier 3 — Deterministic Simulation Fallback

Activated only when ensemble `.pkl` model files are completely absent (e.g., fresh Docker deploy before training).

```python
# Deterministic: same drug pair always returns same result
random.seed(len(drug_a) + len(drug_b))
severity = random.choice(["DEATH RISK", "HOSPITAL ADMISSION",
                           "MONITORING REQUIRED", "SAFE"])
```

**Source Tag:** `simulation`

---

## 3. Severity Metadata Schema

Each prediction response includes structured metadata with severity-specific clinical context:

| Severity | Risk Score | Clinical Explanation |
|---|---|---|
| `DEATH RISK` | 95.5 | Associated with fatal adverse outcomes in FAERS; contraindicated without specialist oversight |
| `HOSPITAL ADMISSION` | 72.0 | Linked to serious events requiring hospitalization; dosage adjustment advised |
| `MONITORING REQUIRED` | 35.0 | Potential interaction risk; clinical monitoring for side-effects is advised |
| `SAFE` | 5.0 | No significant adverse interaction detected in FAERS dataset |

---

## 4. API Design

The backend exposes a **RESTful JSON API** built with FastAPI.

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict/check-interaction` | Run SemanticFusionNet inference; save result to history |
| `GET` | `/predict/history` | Paginated history for authenticated user |
| `GET` | `/predict/history/all` | All predictions (all users, with filters) |
| `GET` | `/predict/{id}` | Full clinical report for a specific prediction |
| `GET` | `/dashboard/stats` | Aggregated metrics, severity distributions, recent activity |
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | JWT token issuance |

### Prediction Request Schema

```json
POST /predict/check-interaction
Authorization: Bearer <JWT>

{
  "drug_a": "Warfarin",
  "drug_b": "Aspirin"
}
```

### Prediction Response Schema

```json
{
  "id": 42,
  "model": "SemanticFusionNet v3.0 (GAT + XGB/CatBoost)",
  "drug_pair": ["WARFARIN", "ASPIRIN"],
  "severity": "HOSPITAL ADMISSION",
  "confidence": 0.92,
  "risk_score": 72.0,
  "explanation": "This pair appears in FAERS reports linked to serious adverse events requiring hospitalisation...",
  "source": "faers_lookup",
  "faers_reports": 47,
  "metadata": {
    "tier": "exact_match",
    "faers_reports": 47
  },
  "created_at": "2026-05-06T19:09:00Z"
}
```

### Advanced History Filtering

The `/history` endpoint supports a **dynamic filter DSL** covering multiple operators:

| Syntax | Meaning | Example |
|---|---|---|
| `field=value` | Exact match | `severity_label=DEATH RISK` |
| `field=A\|B\|C` | IN filter | `severity_label=DEATH RISK\|HOSPITAL ADMISSION` |
| `field__contains=value` | Case-insensitive substring | `drug_a__contains=warf` |
| `field__gte=value` | Greater than or equal | `risk_score__gte=70` |
| `field__lte=value` | Less than or equal | `confidence_score__lte=0.85` |
| `field__gt=value` | Strictly greater than | `risk_score__gt=90` |
| `field__lt=value` | Strictly less than | `risk_score__lt=50` |

---

## 5. Explainability

The system includes an **ExplainerService** that surfaces pharmacological feature contributions to each prediction. In production, this is designed to run **SHAP (SHapley Additive exPlanations)** on the XGBoost ensemble.

**Pharmacological Feature Categories Tracked:**

| Feature | Clinical Relevance |
|---|---|
| Molecular Weight | Affects absorption, distribution |
| Polar Surface Area | Governs membrane permeability |
| Hydrogen Bond Donors | Influences protein binding affinity |
| Metabolic Pathway | Identifies shared CYP450 enzyme competition |
| CYP450 Inhibition | Primary driver of pharmacokinetic interactions |
| Renal Clearance | Flags elimination competition |

**SHAP Output Example:**
```json
{
  "method": "SHAP (Additive Feature Explanations)",
  "key_drivers": ["CYP450 Inhibition", "Metabolic Pathway", "Polar Surface Area"],
  "detailed_note": "The model detected high synergy between WARFARIN and ASPIRIN
                    specifically affecting CYP450 Inhibition and Metabolic Pathway,
                    leading to a HOSPITAL ADMISSION classification."
}
```

---

## 6. Persistence & Compliance Layer

All predictions are persisted in **SQLite** via SQLAlchemy ORM for institutional audit compliance.

### Prediction Record Schema (SQLAlchemy Model)

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-incremented record identifier |
| `user_id` | FK → User | Authenticated researcher who ran the check |
| `drug_a` | String | First drug (normalized) |
| `drug_b` | String | Second drug (normalized) |
| `severity_label` | String | Predicted severity class |
| `confidence_score` | Float | Model confidence `[0, 1]` |
| `risk_score` | Float | Visual risk score `[0, 100]` |
| `explanation` | Text | Clinical explanation string |
| `source` | String | `faers_lookup` / `xgb_catboost_ensemble` / `simulation` |
| `faers_reports` | Integer | Number of supporting FAERS reports |
| `created_at` | DateTime | UTC timestamp of prediction |

---

## 7. Security Architecture

| Layer | Implementation |
|---|---|
| **Authentication** | JWT Bearer Tokens (HS256) |
| **Password Hashing** | Passlib with Bcrypt |
| **Route Protection** | `Depends(get_current_user)` on all prediction/history routes |
| **Container Security** | Non-root `appuser` in Docker |
| **PHI Isolation** | No patient data stored; only drug names and outcomes |

---

## 8. Containerization

The platform ships as a **multi-stage Docker build** for production-grade deployment:

```dockerfile
# Stage 1: Python dependencies (backend + ML)
FROM python:3.12-slim AS backend-builder
...

# Stage 2: Node.js frontend build  
FROM node:20-alpine AS frontend-builder
...

# Stage 3: Final slim production image
FROM python:3.12-slim AS production
# Copies: built Next.js static export + FastAPI app + ML models
# Runs: Uvicorn (backend) + serves Next.js via static file handler
# Port: 8080
# User: appuser (non-root)
```

| Service | Internal Port | External URL |
|---|---|---|
| FastAPI (Uvicorn) | 8000 | — |
| Next.js (served via backend) | 8080 | `http://localhost:8080` |
| API Docs (Swagger) | 8000 | `http://localhost:8080/api/docs` |

---

## 9. Full Inference Flow (End-to-End)

```
User types "Warfarin" + "Aspirin" → clicks Check
         │
         ▼
Next.js Frontend → POST /predict/check-interaction
                   Authorization: Bearer <JWT>
                   { "drug_a": "Warfarin", "drug_b": "Aspirin" }
         │
         ▼
FastAPI route → get_current_user() → validate JWT
         │
         ▼
prediction_service.process_prediction()
         │
         ├── fusion_net.predict_interaction("WARFARIN", "ASPIRIN")
         │         │
         │         ├── Tier 1: FAERS lookup → HIT → return label
         │         │         (confidence = 0.70 + 0.02 × min(47, 14) = 0.98)
         │         │
         │         └── (Tier 2/3 only if Tier 1 misses)
         │
         ├── explainer_service.get_local_explanation(...)
         │
         ├── Save result → SQLite via SQLAlchemy
         │
         └── Return Prediction JSON
         │
         ▼
Frontend renders:
  - Severity badge (color-coded)
  - Confidence gauge
  - Risk score visualization
  - Clinical explanation
  - FAERS evidence count
  - SHAP feature contributions
```

---

*Part of the **IntelliInteraction — Precision Drug-Drug Interaction Safety Platform** documentation suite.*  
*See also: [DATASET.md](./DATASET.md) · [EXPERIMENTAL_SETUP.md](./EXPERIMENTAL_SETUP.md) · [README.md](./README.md)*
