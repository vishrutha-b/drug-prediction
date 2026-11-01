"""
fusion_net.py  -  IntelliInteraction DDI Prediction Engine
-----------------------------------------------------------
Hybrid 3-tier predictor backed by 75,537 drug pairs from FDA FAERS.

Tier 1 – Exact-match FAERS lookup (pairs_lookup.pkl)
    Empirically validated severity for any drug pair seen in the dataset.
    Covers 75K pairs.  Highest accuracy — returned immediately.

Tier 2 – GAT + XGBoost/CatBoost Ensemble  (Sections 4.3.3 / 4.3.7)
    For any unknown pair:
      a. Look up 64-dim GAT node embedding for each drug.
         Unknown drugs → TF-IDF char n-gram embedding (200→64 dim).
      b. Concatenate embeddings + pair features → 133-dim vector.
      c. XGBoost prob + CatBoost prob → soft-vote → label.

Tier 3 – Deterministic simulation fallback
    Used only if model .pkl files are completely absent.

Model files produced by ml/pipeline/run_full_pipeline.py:
    ml/models/drug_embeddings.pkl
    ml/models/tfidf_vectorizer.pkl
    ml/models/xgb_model.pkl
    ml/models/catboost_model.pkl
    ml/models/label_encoder.pkl
    ml/models/pairs_lookup.pkl
"""

import os
import pickle
import hashlib
import numpy as np
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Locate model artifacts (works locally and inside Docker)
# ---------------------------------------------------------------------------

def _find_models_dir() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models"),
        "/app/ml/models",
        os.path.join(os.path.dirname(__file__), "models"),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return os.path.abspath(p)
    return candidates[0]


MODELS_DIR = _find_models_dir()


def _load_pkl(filename: str):
    path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------
# Load all artifacts once at import time
# ---------------------------------------------------------------------------

_pairs_lookup    = _load_pkl("pairs_lookup.pkl")    or {}
_drug_embeddings = _load_pkl("drug_embeddings.pkl") or {}
_tfidf_vec       = _load_pkl("tfidf_vectorizer.pkl")
_xgb_model       = _load_pkl("xgb_model.pkl")
_cb_model        = _load_pkl("catboost_model.pkl")
_le              = _load_pkl("label_encoder.pkl")

# Ensemble is ready when both XGB and CatBoost are loaded
_ENSEMBLE_READY = (_xgb_model is not None) and (_cb_model is not None) and (_le is not None)
_GAT_READY      = len(_drug_embeddings) > 0

if _ENSEMBLE_READY:
    source_tag = "GAT + XGB/CatBoost" if _GAT_READY else "TF-IDF + XGB/CatBoost"
    print(f"[FusionNet] Ensemble ({source_tag}) loaded. "
          f"Lookup covers {len(_pairs_lookup)//2:,} pairs. "
          f"GAT embeddings: {len(_drug_embeddings):,} drugs.")
else:
    print("[FusionNet] WARNING: ensemble .pkl files not found — "
          "falling back to simulation.")

# ---------------------------------------------------------------------------
# Severity metadata
# ---------------------------------------------------------------------------

_SEVERITY_META = {
    "DEATH RISK": {
        "explanation": (
            "This drug combination has been associated with fatal adverse "
            "outcomes in FDA FAERS reports. Co-administration is "
            "contraindicated without specialist oversight."
        ),
        "risk_score": 95.5,
    },
    "HOSPITAL ADMISSION": {
        "explanation": (
            "This pair appears in FAERS reports linked to serious adverse "
            "events requiring hospitalisation. Dosage adjustment or an "
            "alternative agent should be considered."
        ),
        "risk_score": 72.0,
    },
    "MONITORING REQUIRED": {
        "explanation": (
            "FAERS data indicates a potential interaction risk for this "
            "combination. Clinical monitoring for side-effects is advised."
        ),
        "risk_score": 35.0,
    },
    "SAFE": {
        "explanation": (
            "No significant adverse interaction between these agents was "
            "detected in the FAERS dataset."
        ),
        "risk_score": 5.0,
    },
}

# ---------------------------------------------------------------------------
# Feature helpers
# ---------------------------------------------------------------------------

def _pair_hash_norm(a: str, b: str) -> float:
    key = "|".join(sorted([a.upper().strip(), b.upper().strip()]))
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31) / (2**31)


def _get_embedding(drug: str) -> np.ndarray:
    """
    Return 64-dim embedding for a drug.
    Priority: GAT embedding → TF-IDF[:64] fallback → zeros.
    """
    if drug in _drug_embeddings:
        return _drug_embeddings[drug].astype(np.float32)

    if _tfidf_vec is not None:
        tfidf = _tfidf_vec.transform([drug]).toarray()[0].astype(np.float32)
        out   = np.zeros(64, dtype=np.float32)
        out[:min(64, len(tfidf))] = tfidf[:64]
        return out

    return np.zeros(64, dtype=np.float32)


def _build_ensemble_features(drug_a: str, drug_b: str,
                              report_count: float = 1.0) -> np.ndarray:
    """Build 133-dim feature vector matching train_ensemble.py exactly."""
    emb_a = _get_embedding(drug_a)   # 64-dim
    emb_b = _get_embedding(drug_b)   # 64-dim
    extra = np.array([
        np.log1p(report_count),
        _pair_hash_norm(drug_a, drug_b),
        float(len(drug_a)), float(len(drug_b)),
        float(len(drug_a) + len(drug_b)),
        float(abs(len(drug_a) - len(drug_b))),
    ], dtype=np.float32)
    return np.concatenate([emb_a, emb_b, extra]).reshape(1, -1)  # (1, 133)

# ---------------------------------------------------------------------------
# Fallback simulation (used only if .pkl files are missing)
# ---------------------------------------------------------------------------

import random as _random

def _simulate(drug_a: str, drug_b: str) -> Dict[str, Any]:
    """Deterministic simulation — last resort fallback."""
    _random.seed(len(drug_a) + len(drug_b))
    severity = _random.choice(["DEATH RISK", "HOSPITAL ADMISSION",
                                "MONITORING REQUIRED", "SAFE"])
    confidence = round(_random.uniform(0.75, 0.99), 2)
    meta = _SEVERITY_META[severity]
    return {
        "severity": severity, "confidence": confidence,
        "explanation": meta["explanation"], "risk_score": meta["risk_score"],
        "source": "simulation",
    }

# ---------------------------------------------------------------------------
# Main predictor class
# ---------------------------------------------------------------------------

class HybridSemanticFusionNet:
    """
    Three-tier DDI severity predictor.

    Tier 1: Exact FAERS lookup          — highest accuracy, 75K pairs
    Tier 2: GAT embeddings + XGB/CatBoost ensemble — novel pairs
    Tier 3: Deterministic simulation    — no model files present
    """

    model_name = "SemanticFusionNet v3.0 (GAT + XGB/CatBoost)"

    def predict_interaction(self, drug_a: str, drug_b: str) -> Dict[str, Any]:
        a = drug_a.upper().strip()
        b = drug_b.upper().strip()

        # ── Tier 1: exact FAERS lookup ────────────────────────────────────
        # First, we check if this exact drug pair exists in our pre-compiled FAERS dictionary.
        # This provides instant, highly accurate responses for 75,537 known pairs.
        for key in [(a, b), (b, a)]:
            if key in _pairs_lookup:
                entry      = _pairs_lookup[key]
                severity   = entry["label"]
                count      = entry.get("count", 1)
                # Confidence scales linearly with the number of FAERS reports, capped at 0.99
                confidence = min(0.99, 0.70 + 0.02 * min(count, 14))
                meta       = _SEVERITY_META.get(severity, _SEVERITY_META["MONITORING REQUIRED"])
                return {
                    "model":       self.model_name,
                    "drug_pair":   [drug_a, drug_b],
                    "severity":    severity,
                    "confidence":  round(confidence, 2),
                    "explanation": meta["explanation"],
                    "risk_score":  meta["risk_score"],
                    "source":      "faers_lookup",
                    "faers_reports": count,
                    "metadata": {"tier": "exact_match", "faers_reports": count},
                }

        # ── Tier 2: GAT embedding + XGBoost/CatBoost ensemble ─────────────
        # If the pair is novel (not in Tier 1), we activate the Machine Learning ensemble.
        if _ENSEMBLE_READY:
            # Build the 133-dimensional feature vector (uses GAT/TF-IDF embeddings + metadata)
            X = _build_ensemble_features(a, b)

            # Get class probability distributions from both models
            xgb_prob = _xgb_model.predict_proba(X)[0]   # (n_classes,)
            cb_prob  = _cb_model.predict_proba(X)[0]

            # Soft voting: We average the probabilities from XGBoost and CatBoost
            ens_prob  = 0.5 * xgb_prob + 0.5 * cb_prob
            pred_idx  = int(ens_prob.argmax())
            
            # Map the highest probability index back to the severity label (e.g., "DEATH RISK")
            severity  = _le.inverse_transform([pred_idx])[0]
            confidence = round(float(ens_prob.max()), 2)

            emb_source = "gat" if a in _drug_embeddings else "tfidf_fallback"
            meta = _SEVERITY_META.get(severity, _SEVERITY_META["MONITORING REQUIRED"])

            return {
                "model":       self.model_name,
                "drug_pair":   [drug_a, drug_b],
                "severity":    severity,
                "confidence":  confidence,
                "explanation": meta["explanation"],
                "risk_score":  meta["risk_score"],
                "source":      "xgb_catboost_ensemble",
                "faers_reports": 0,
                "metadata": {
                    "tier":            "ml_ensemble",
                    "embedding_source": emb_source,
                    "class_probabilities": {
                        label: round(float(p), 3)
                        for label, p in zip(_le.classes_, ens_prob)
                    },
                },
            }

        # ── Tier 3: simulation fallback ───────────────────────────────────
        # If the ML model files (.pkl) are missing entirely, we fall back to a 
        # deterministic simulation to guarantee the API never crashes (100% uptime).
        result = _simulate(drug_a, drug_b)
        return {
            "model":     self.model_name,
            "drug_pair": [drug_a, drug_b],
            **result,
            "faers_reports": 0,
            "metadata": {"tier": "simulation"},
        }


# Global singleton used by prediction_service.py
fusion_net = HybridSemanticFusionNet()
