"""
run_full_pipeline.py
--------------------
Master training script.  Runs all phases in order:

  Step 1 : preprocess   >> ml/data/faers_pairs_clean.csv
  Step 2 : train_gat    >> tfidf_vectorizer.pkl, drug_node_map.pkl,
                          gat_weights.pt, drug_embeddings.pkl
  Step 3 : train_ensemble >> xgb_model.pkl, catboost_model.pkl,
                            label_encoder.pkl

Usage
-----
  cd "drug prediction"
  python ml/pipeline/run_full_pipeline.py
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


import os, sys, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
EMB_PATH   = os.path.join(MODELS_DIR, "drug_embeddings.pkl")


def banner(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def step1_preprocess():
    banner("STEP 1 -- Data Preprocessing (Section 4.3.1)")
    from preprocess import preprocess
    df = preprocess()
    return df


def step2_train_gat():
    banner("STEP 2 -- GAT Training (Sections 4.3.3 / 4.3.8)")
    from train_gat import train
    train()


def step3_train_ensemble():
    banner("STEP 3 -- XGBoost + CatBoost Ensemble (Section 4.3.7)")
    from train_ensemble import train
    train()


if __name__ == "__main__":
    t_start = time.time()

    step1_preprocess()

    # Check if torch_geometric is available for GAT
    gat_ok = False
    try:
        import torch
        import torch_geometric
        gat_ok = True
        print("\n[Pipeline] torch + torch_geometric detected -- running GAT training.")
    except ImportError as e:
        print(f"\n[Pipeline] WARNING: GAT skipped ({e}).")
        print("[Pipeline] Falling back to TF-IDF embeddings for the ensemble.")
        # Generate TF-IDF embeddings + node map without GAT
        import pandas as pd, pickle
        from embedding import fit_vectorizer, embed_all_drugs, save_vectorizer
        from graph_builder import save_node_map

        data_dir  = os.path.join(BASE_DIR, "..", "data")
        clean_csv = os.path.join(data_dir, "faers_pairs_clean.csv")
        df = pd.read_csv(clean_csv)

        vec  = fit_vectorizer(df)
        save_vectorizer(vec)
        embs = embed_all_drugs(df, vec)

        # Build basic drug_to_idx map without PyG
        all_drugs   = sorted(set(df["drug_a"].tolist() + df["drug_b"].tolist()))
        drug_to_idx = {d: i for i, d in enumerate(all_drugs)}
        save_node_map(drug_to_idx)

        # Save 64-dim TF-IDF[:64] embeddings as fallback drug_embeddings.pkl
        import numpy as np
        os.makedirs(MODELS_DIR, exist_ok=True)
        drug_embeddings_fallback = {}
        for drug, emb in embs.items():
            out = np.zeros(64, dtype="float32")
            out[:min(64, len(emb))] = emb[:64]
            drug_embeddings_fallback[drug] = out
        with open(EMB_PATH, "wb") as f:
            pickle.dump(drug_embeddings_fallback, f)
        print(f"[Pipeline] Fallback embeddings saved >> {EMB_PATH}")

    if gat_ok:
        step2_train_gat()

    step3_train_ensemble()

    elapsed = time.time() - t_start
    banner(f"PIPELINE COMPLETE  ({elapsed/60:.1f} minutes)")
    print("  Model files are in ml/models/")
    print("  Restart the backend to load the new models.\n")
