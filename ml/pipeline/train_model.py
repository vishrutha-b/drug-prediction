"""
train_model.py
--------------
Trains a RandomForest DDI severity classifier on the FAERS pair dataset
produced by faers_fetcher.py.

Outputs
-------
ml/models/ddi_model.pkl       - trained RandomForest classifier
ml/models/pairs_lookup.pkl    - exact-match lookup dict for known FAERS pairs
ml/models/label_encoder.pkl   - LabelEncoder for the severity classes

Usage
-----
  cd "drug prediction"
  python ml/pipeline/train_model.py
"""

import os
import sys
import pickle
import hashlib

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, "..", "data", "faers_pairs.csv")
MODELS_DIR  = os.path.join(BASE_DIR, "..", "models")

SEVERITY_RANK = {
    "DEATH RISK":          3,
    "HOSPITAL ADMISSION":  2,
    "MONITORING REQUIRED": 1,
    "SAFE":                0,
}

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _pair_hash(drug_a: str, drug_b: str) -> int:
    """Deterministic numeric hash of the normalised drug pair."""
    key = "|".join(sorted([drug_a.upper().strip(), drug_b.upper().strip()]))
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)


def _drug_features(name: str) -> dict:
    """Character-level features for a single drug name."""
    n = name.upper().strip()
    return {
        "len":       len(n),
        "num_words": len(n.split()),
        "has_digit": int(any(c.isdigit() for c in n)),
        "has_paren": int("(" in n),
    }


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build numeric feature matrix from the pair dataframe."""
    rows = []
    for _, r in df.iterrows():
        a, b  = str(r["drug_a"]), str(r["drug_b"])
        fa    = _drug_features(a)
        fb    = _drug_features(b)
        count    = float(r.get("report_count", 1))
        log_cnt  = np.log1p(count)
        rows.append({
            "pair_hash":    _pair_hash(a, b),
            "log_count":    log_cnt,
            "report_count": count,
            "a_len":        fa["len"],
            "a_words":      fa["num_words"],
            "a_digit":      fa["has_digit"],
            "a_paren":      fa["has_paren"],
            "b_len":        fb["len"],
            "b_words":      fb["num_words"],
            "b_digit":      fb["has_digit"],
            "b_paren":      fb["has_paren"],
            "len_sum":      fa["len"] + fb["len"],
            "len_diff":     abs(fa["len"] - fb["len"]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------

def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    # 1. Load data
    print(f"Loading data from {DATA_PATH} ...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run faers_fetcher.py first."
        )
    df = pd.read_csv(DATA_PATH)
    print(f"  Loaded {len(df):,} rows.")
    print(f"  Severity distribution:\n{df['severity_label'].value_counts()}\n")

    # 2. Build exact-match lookup (for known FAERS pairs)
    print("Building exact-match lookup dict ...")
    pairs_lookup: dict = {}
    for _, r in df.iterrows():
        key = (r["drug_a"].upper().strip(), r["drug_b"].upper().strip())
        rev = (key[1], key[0])
        existing_rank = SEVERITY_RANK.get(
            pairs_lookup.get(key, {}).get("label", ""), -1
        )
        new_rank = SEVERITY_RANK.get(r["severity_label"], 0)
        if new_rank > existing_rank:
            payload = {
                "label": r["severity_label"],
                "count": int(r.get("report_count", 1)),
            }
            pairs_lookup[key] = payload
            pairs_lookup[rev] = payload   # bidirectional
    print(f"  Lookup covers {len(pairs_lookup) // 2:,} unique pairs.\n")

    # 3. Feature engineering
    print("Building features ...")
    X  = build_features(df)
    le = LabelEncoder()
    y  = le.fit_transform(df["severity_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train RandomForest
    print("Training RandomForest classifier ...")
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    clf.fit(X_train, y_train)

    # 5. Evaluation
    y_pred = clf.predict(X_test)
    print("\n--- Test-set Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    cv_scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"5-fold CV accuracy: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}\n")

    # 6. Feature importances
    importance_df = pd.DataFrame({
        "feature":    X.columns,
        "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)
    print("Top feature importances:")
    print(importance_df.head(8).to_string(index=False))
    print()

    # 7. Save artifacts
    model_path   = os.path.join(MODELS_DIR, "ddi_model.pkl")
    lookup_path  = os.path.join(MODELS_DIR, "pairs_lookup.pkl")
    encoder_path = os.path.join(MODELS_DIR, "label_encoder.pkl")

    with open(model_path,   "wb") as f: pickle.dump(clf,          f)
    with open(lookup_path,  "wb") as f: pickle.dump(pairs_lookup, f)
    with open(encoder_path, "wb") as f: pickle.dump(le,           f)

    print(f"[OK] Saved model   >> {model_path}")
    print(f"[OK] Saved lookup  >> {lookup_path}")
    print(f"[OK] Saved encoder >> {encoder_path}")
    print("\nModel is ready. Rebuild Docker to bundle the .pkl files.")


if __name__ == "__main__":
    train()
