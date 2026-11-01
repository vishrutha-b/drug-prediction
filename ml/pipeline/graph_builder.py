"""
graph_builder.py
----------------
Section 4.3.3 - Graph-Based Interaction Modeling.

Builds a drug interaction graph from the cleaned FAERS pair dataset:
  Nodes = unique drugs    (feature: TF-IDF 200-dim embedding)
  Edges = FAERS drug pairs (bidirectional)

Node labels = worst severity the drug is involved in (used as the
GAT node-classification training signal).

Converts to a torch_geometric.data.Data object for GAT training.
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


import os
import pickle
import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

CLEAN_CSV = os.path.join(DATA_DIR, "faers_pairs_clean.csv")
MAP_PATH  = os.path.join(MODELS_DIR, "drug_node_map.pkl")

SEVERITY_RANK = {
    "DEATH RISK": 3, "HOSPITAL ADMISSION": 2,
    "MONITORING REQUIRED": 1, "SAFE": 0,
}


def build_graph(df: pd.DataFrame, tfidf_embeddings: dict) -> tuple:
    """
    Returns (pyg_data, drug_to_idx).
    pyg_data.y = per-node worst severity label (0-3) for GAT training.
    """
    print("[GraphBuilder] Building drug interaction graph …")

    all_drugs = sorted(set(df["drug_a"].tolist() + df["drug_b"].tolist()))
    drug_to_idx = {d: i for i, d in enumerate(all_drugs)}
    n_nodes = len(all_drugs)
    print(f"  Nodes (unique drugs): {n_nodes:,}")
    print(f"  Edges (FAERS pairs):  {len(df):,}")

    # Node feature matrix: TF-IDF embeddings
    emb_dim = next(iter(tfidf_embeddings.values())).shape[0]
    x = np.zeros((n_nodes, emb_dim), dtype=np.float32)
    for drug, idx in drug_to_idx.items():
        if drug in tfidf_embeddings:
            x[idx] = tfidf_embeddings[drug]

    # Node labels: worst severity this drug participates in
    node_ranks = np.zeros(n_nodes, dtype=np.int64)
    for _, row in df.iterrows():
        rank = SEVERITY_RANK.get(row["severity_label"], 0)
        ia   = drug_to_idx[row["drug_a"]]
        ib   = drug_to_idx[row["drug_b"]]
        node_ranks[ia] = max(node_ranks[ia], rank)
        node_ranks[ib] = max(node_ranks[ib], rank)

    # Bidirectional edge index
    src, dst = [], []
    for _, row in df.iterrows():
        a = drug_to_idx[row["drug_a"]]
        b = drug_to_idx[row["drug_b"]]
        src.extend([a, b])
        dst.extend([b, a])

    data = Data(
        x          = torch.from_numpy(x),
        edge_index = torch.tensor([src, dst], dtype=torch.long),
        y          = torch.from_numpy(node_ranks),
    )
    print(f"  PyG graph: {data.num_nodes} nodes, {data.num_edges} edges, "
          f"feature dim {data.x.shape[1]}")
    return data, drug_to_idx


def save_node_map(drug_to_idx: dict, path: str = MAP_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(drug_to_idx, f)
    print(f"  Node map saved >> {path}  ({len(drug_to_idx):,} entries)")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from embedding import load_vectorizer, embed_all_drugs
    df  = pd.read_csv(CLEAN_CSV)
    vec = load_vectorizer()
    embs = embed_all_drugs(df, vec)
    data, drug_to_idx = build_graph(df, embs)
    save_node_map(drug_to_idx)
    print("Graph built successfully.")
