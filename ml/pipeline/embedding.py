"""
embedding.py
------------
Section 4.3.2 - Semantic Feature Extraction.

Fits a TF-IDF character n-gram vectorizer (3-5 char n-grams, 200-dim)
on all unique drug names from the FAERS dataset.  Character n-grams
capture morphological similarity between drug names (e.g. "Warfarin"
vs "Warfarine", "Atorvastatin" vs "Rosuvastatin").

Outputs
-------
ml/models/tfidf_vectorizer.pkl   - fitted vectorizer (for serving)
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

CLEAN_CSV     = os.path.join(DATA_DIR, "faers_pairs_clean.csv")
VEC_PATH      = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
EMBEDDING_DIM = 200   # TF-IDF max_features >> 200-dim per drug name


def fit_vectorizer(df: pd.DataFrame) -> TfidfVectorizer:
    """Fit TF-IDF char n-gram vectorizer on all unique drug names."""
    all_drugs = pd.concat([df["drug_a"], df["drug_b"]]).unique()
    print(f"[Embedding] Fitting TF-IDF on {len(all_drugs):,} unique drug names …")

    vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=EMBEDDING_DIM,
        sublinear_tf=True,
    )
    vec.fit(all_drugs)
    print(f"  Output dim: {EMBEDDING_DIM}")
    return vec


def embed_drug(name: str, vec: TfidfVectorizer) -> np.ndarray:
    """Return 200-dim float32 embedding for a single drug name."""
    return vec.transform([name]).toarray()[0].astype(np.float32)


def embed_all_drugs(df: pd.DataFrame, vec: TfidfVectorizer) -> dict:
    """Return {drug_name: 200-dim ndarray} for every unique drug."""
    all_drugs = pd.concat([df["drug_a"], df["drug_b"]]).unique()
    print(f"[Embedding] Generating embeddings for {len(all_drugs):,} drugs …")
    return {name: embed_drug(name, vec) for name in all_drugs}


def save_vectorizer(vec: TfidfVectorizer, path: str = VEC_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(vec, f)
    print(f"  Vectorizer saved >> {path}")


def load_vectorizer(path: str = VEC_PATH) -> TfidfVectorizer:
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_CSV)
    vec = fit_vectorizer(df)
    save_vectorizer(vec)
    # Quick test
    v = embed_drug("WARFARIN", vec)
    print(f"  WARFARIN embedding shape: {v.shape}, norm: {np.linalg.norm(v):.3f}")
