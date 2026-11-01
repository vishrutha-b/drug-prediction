"""
train_ensemble.py
-----------------
Section 4.3.7 / 4.3.8 - XGBoost + CatBoost Soft-Voting Ensemble.

Feature vector per drug pair (133 features total):
  [GAT_emb_a (64) | GAT_emb_b (64) | log_count | pair_hash_norm |
   a_len | b_len | len_sum | len_diff]

For drugs not in the GAT embedding dict (unknown at serving time),
TF-IDF[:64] is used as a fallback embedding.

Soft voting:  final_prob = 0.5 × xgb_prob + 0.5 × catboost_prob

Outputs
-------
ml/models/xgb_model.pkl
ml/models/catboost_model.pkl
ml/models/label_encoder.pkl
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


import os, sys, pickle, hashlib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
from catboost import CatBoostClassifier

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

CLEAN_CSV = os.path.join(DATA_DIR, "faers_pairs_clean.csv")
EMB_PATH  = os.path.join(MODELS_DIR, "drug_embeddings.pkl")
VEC_PATH  = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")


def _pair_hash(a: str, b: str) -> float:
    key = "|".join(sorted([a.upper().strip(), b.upper().strip()]))
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31) / (2**31)


def _get_embedding(drug: str, drug_embs: dict, vec) -> np.ndarray:
    """GAT embedding (64-dim) if available, else TF-IDF[:64] fallback."""
    if drug in drug_embs:
        return drug_embs[drug]
    tfidf = vec.transform([drug]).toarray()[0].astype(np.float32)
    # Pad or trim to 64-dim
    out = np.zeros(64, dtype=np.float32)
    out[:min(64, len(tfidf))] = tfidf[:64]
    return out


def build_features(df: pd.DataFrame, drug_embs: dict, vec) -> np.ndarray:
    """Build (n_pairs × 133) feature matrix."""
    rows = []
    for _, r in df.iterrows():
        a, b  = str(r["drug_a"]), str(r["drug_b"])
        emb_a = _get_embedding(a, drug_embs, vec)   # 64
        emb_b = _get_embedding(b, drug_embs, vec)   # 64
        count = float(r.get("report_count", 1))
        extra = np.array([
            np.log1p(count),
            _pair_hash(a, b),
            float(len(a)), float(len(b)),
            float(len(a) + len(b)),
            float(abs(len(a) - len(b))),
        ], dtype=np.float32)
        rows.append(np.concatenate([emb_a, emb_b, extra]))
    return np.array(rows, dtype=np.float32)


def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Load data + artifacts ─────────────────────────────────────────────
    print("[Ensemble] Loading cleaned data …")
    df = pd.read_csv(CLEAN_CSV)
    print(f"  Rows: {len(df):,}")

    with open(EMB_PATH, "rb") as f:
        drug_embs = pickle.load(f)
    print(f"  GAT embeddings: {len(drug_embs):,} drugs")

    with open(VEC_PATH, "rb") as f:
        vec = pickle.load(f)

    # ── Feature matrix ────────────────────────────────────────────────────
    print("[Ensemble] Building feature matrix (133-dim per pair) …")
    X  = build_features(df, drug_embs, vec)
    le = LabelEncoder()
    y  = le.fit_transform(df["severity_label"])
    print(f"  X shape: {X.shape}  |  Classes: {list(le.classes_)}")

    # 80 / 20 stratified split (Section 4.3.5)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train):,}  |  Test: {len(X_test):,}\n")

    # ── 5-Fold Cross Validation ───────────────────────────────────────────
    print("[Ensemble] Running 5-Fold Cross Validation on Training Set …")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    fold_accuracies = []
    fold_precisions = []
    fold_recalls = []
    fold_f1s = []
    fold_aucs = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_f_train, y_f_train = X_train[train_idx], y_train[train_idx]
        X_f_val, y_f_val = X_train[val_idx], y_train[val_idx]
        
        # Fast training for CV
        fold_xgb = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.05, n_jobs=-1, random_state=42)
        fold_xgb.fit(X_f_train, y_f_train, verbose=False)
        
        fold_cb = CatBoostClassifier(iterations=100, depth=6, learning_rate=0.05, random_seed=42, verbose=0)
        fold_cb.fit(X_f_train, y_f_train)
        
        # Evaluate ensemble on fold validation set
        ens_prob = 0.5 * fold_xgb.predict_proba(X_f_val) + 0.5 * fold_cb.predict_proba(X_f_val)
        ens_preds = ens_prob.argmax(axis=1)
        
        fold_acc = accuracy_score(y_f_val, ens_preds)
        fold_prec = precision_score(y_f_val, ens_preds, average='weighted', zero_division=0)
        fold_rec = recall_score(y_f_val, ens_preds, average='weighted', zero_division=0)
        fold_f1 = f1_score(y_f_val, ens_preds, average='weighted', zero_division=0)
        
        # ROC AUC for multi-class requires ovr (One-vs-Rest)
        try:
            fold_auc = roc_auc_score(y_f_val, ens_prob, multi_class='ovr', average='weighted')
        except ValueError:
            fold_auc = 0.0 # Fallback if a fold completely misses a class
            
        print(f"  Fold {fold+1} | Acc: {fold_acc:.3f} | Prec: {fold_prec:.3f} | Rec: {fold_rec:.3f} | F1: {fold_f1:.3f} | AUC: {fold_auc:.3f}")
        
        fold_accuracies.append(fold_acc)
        fold_precisions.append(fold_prec)
        fold_recalls.append(fold_rec)
        fold_f1s.append(fold_f1)
        fold_aucs.append(fold_auc)
        
    print("\n  --- Average 5-Fold CV Metrics ---")
    print(f"  Accuracy : {np.mean(fold_accuracies):.3f} (±{np.std(fold_accuracies):.3f})")
    print(f"  Precision: {np.mean(fold_precisions):.3f} (±{np.std(fold_precisions):.3f})")
    print(f"  Recall   : {np.mean(fold_recalls):.3f} (±{np.std(fold_recalls):.3f})")
    print(f"  F1 Score : {np.mean(fold_f1s):.3f} (±{np.std(fold_f1s):.3f})")
    print(f"  ROC-AUC  : {np.mean(fold_aucs):.3f} (±{np.std(fold_aucs):.3f})\n")

    # ── XGBoost ───────────────────────────────────────────────────────────
    print("[Ensemble] Training XGBoost (400 estimators) …")
    xgb_model = xgb.XGBClassifier(
        n_estimators=400, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric="mlogloss", n_jobs=-1, random_state=42,
    )
    xgb_model.fit(X_train, y_train,
                  eval_set=[(X_test, y_test)], verbose=50)
    xgb_proba = xgb_model.predict_proba(X_test)
    print(f"  XGBoost test accuracy: {accuracy_score(y_test, xgb_proba.argmax(1)):.3f}")

    # ── CatBoost ──────────────────────────────────────────────────────────
    print("\n[Ensemble] Training CatBoost (400 iterations) …")
    cb_model = CatBoostClassifier(
        iterations=400, depth=6, learning_rate=0.05,
        eval_metric="Accuracy", random_seed=42, verbose=50,
    )
    cb_model.fit(X_train, y_train, eval_set=(X_test, y_test))
    cb_proba = cb_model.predict_proba(X_test)
    print(f"  CatBoost test accuracy: {accuracy_score(y_test, cb_proba.argmax(1)):.3f}")

    # ── Soft-voting ensemble ──────────────────────────────────────────────
    ens_proba = 0.5 * xgb_proba + 0.5 * cb_proba
    ens_preds = ens_proba.argmax(axis=1)
    print(f"\n[Ensemble] Soft-voting accuracy: {accuracy_score(y_test, ens_preds):.3f}")
    print("\n--- Classification Report (XGBoost + CatBoost Ensemble) ---")
    print(classification_report(y_test, ens_preds, target_names=le.classes_))

    # ── Save artifacts ────────────────────────────────────────────────────
    paths = {
        "xgb_model.pkl":      xgb_model,
        "catboost_model.pkl": cb_model,
        "label_encoder.pkl":  le,
    }
    for fname, obj in paths.items():
        p = os.path.join(MODELS_DIR, fname)
        with open(p, "wb") as f:
            pickle.dump(obj, f)
        print(f"  Saved >> {p}")

    print("\n[Ensemble] Done. Rebuild Docker to bundle new model files.")


if __name__ == "__main__":
    train()
