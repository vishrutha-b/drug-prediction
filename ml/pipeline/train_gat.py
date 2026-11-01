"""
train_gat.py
------------
Section 4.3.8 - Compiles and trains the GAT model.

Optimizer  : Adam (lr=0.005, weight_decay=5e-4)
Epochs     : up to 200 with early stopping (patience=20)
Task       : Node-level severity classification (4 classes)
Class wts  : Inverse-frequency weights to handle imbalance (Section 4.3.1)

Outputs
-------
ml/models/gat_weights.pt       - best model state dict
ml/models/drug_embeddings.pkl  - {drug_name: 64-dim np.ndarray}
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


import os, sys, pickle, time
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from gat_model import GATEncoder

DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
CLEAN_CSV  = os.path.join(DATA_DIR, "faers_pairs_clean.csv")

WEIGHTS_PATH = os.path.join(MODELS_DIR, "gat_weights.pt")
EMB_PATH     = os.path.join(MODELS_DIR, "drug_embeddings.pkl")

# Hyper-parameters
NUM_CLASSES  = 4
HIDDEN       = 128
HEADS        = 4
DROPOUT      = 0.3
LR           = 0.005
WEIGHT_DECAY = 5e-4
EPOCHS       = 200
PATIENCE     = 20


def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── 1. Load cleaned data ──────────────────────────────────────────────
    print(f"[GAT Train] Loading {CLEAN_CSV} …")
    df = pd.read_csv(CLEAN_CSV)

    # ── 2. TF-IDF embeddings ──────────────────────────────────────────────
    from embedding import fit_vectorizer, embed_all_drugs, save_vectorizer
    vec = fit_vectorizer(df)
    save_vectorizer(vec)
    tfidf_embs = embed_all_drugs(df, vec)

    # ── 3. Build PyG graph ────────────────────────────────────────────────
    from graph_builder import build_graph, save_node_map
    data, drug_to_idx = build_graph(df, tfidf_embs)
    save_node_map(drug_to_idx)
    idx_to_drug = {v: k for k, v in drug_to_idx.items()}

    # ── 4. Train / val masks (80/20) ──────────────────────────────────────
    n    = data.num_nodes
    perm = torch.randperm(n, generator=torch.Generator().manual_seed(42))
    split = int(0.8 * n)
    train_mask = torch.zeros(n, dtype=torch.bool)
    val_mask   = torch.zeros(n, dtype=torch.bool)
    train_mask[perm[:split]] = True
    val_mask[perm[split:]]   = True
    data.train_mask = train_mask
    data.val_mask   = val_mask

    # ── 5. Class weights (handle imbalance) ───────────────────────────────
    counts = torch.bincount(data.y[train_mask], minlength=NUM_CLASSES).float()
    class_weights = (counts.sum() / (NUM_CLASSES * counts + 1e-6))

    # ── 6. Model + optimizer ──────────────────────────────────────────────
    in_channels = data.x.shape[1]
    model = GATEncoder(in_channels, NUM_CLASSES, HIDDEN, HEADS, DROPOUT)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY
    )

    print(f"\n[GAT Train] Architecture:")
    print(f"  GATConv({in_channels} >> {HIDDEN}×{HEADS}) >> ELU >> GATConv(>> 64) >> Linear({NUM_CLASSES})")
    print(f"  Train nodes: {train_mask.sum():,}  |  Val nodes: {val_mask.sum():,}")
    print(f"  Class weights: {class_weights.tolist()}\n")

    best_val_acc = 0.0
    best_epoch   = 0
    patience_ctr = 0
    t0 = time.time()

    for epoch in range(1, EPOCHS + 1):
        # Training step
        model.train()
        optimizer.zero_grad()
        out  = model(data.x, data.edge_index)
        loss = F.cross_entropy(out[train_mask], data.y[train_mask],
                               weight=class_weights)
        loss.backward()
        optimizer.step()

        # Validation
        model.eval()
        with torch.no_grad():
            logits    = model(data.x, data.edge_index)
            preds     = logits.argmax(dim=1)
            val_acc   = (preds[val_mask]   == data.y[val_mask]).float().mean().item()
            train_acc = (preds[train_mask] == data.y[train_mask]).float().mean().item()

        if epoch % 10 == 0 or epoch == 1:
            print(f"  Epoch {epoch:>3d}/{EPOCHS} | "
                  f"loss={loss.item():.4f} | "
                  f"train_acc={train_acc:.3f} | "
                  f"val_acc={val_acc:.3f} | "
                  f"elapsed={time.time()-t0:.0f}s")

        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch   = epoch
            torch.save(model.state_dict(), WEIGHTS_PATH)
            patience_ctr = 0
        else:
            patience_ctr += 1
            if patience_ctr >= PATIENCE:
                print(f"\n  Early stop at epoch {epoch} "
                      f"(best val_acc={best_val_acc:.3f} @ epoch {best_epoch})")
                break

    print(f"\n[GAT Train] Best val accuracy : {best_val_acc:.3f}")
    print(f"[GAT Train] Weights saved     >> {WEIGHTS_PATH}")

    # ── 7. Extract and save drug embeddings ───────────────────────────────
    print("\n[GAT Train] Extracting 64-dim node embeddings …")
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    model.eval()
    with torch.no_grad():
        all_embs = model.encode(data.x, data.edge_index).numpy()  # (n, 64)

    drug_embeddings = {idx_to_drug[i]: all_embs[i] for i in range(n)}

    with open(EMB_PATH, "wb") as f:
        pickle.dump(drug_embeddings, f)
    print(f"[GAT Train] Embeddings saved  >> {EMB_PATH}  ({len(drug_embeddings):,} drugs)")


if __name__ == "__main__":
    train()
