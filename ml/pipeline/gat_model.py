"""
gat_model.py
------------
Section 4.3.7 – Graph Attention Network (GAT) architecture.

Architecture:
  Layer 1: GATConv(in=200, out=128, heads=4, concat=True)  → 512-dim + ELU
  Dropout: 0.3
  Layer 2: GATConv(in=512, out=64,  heads=1, concat=False) → 64-dim
  Head   : Linear(64 → num_classes)   [training signal only]

The 64-dim output of Layer 2 is saved as the drug embedding used
downstream by the XGBoost + CatBoost ensemble (Section 4.3.8).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv


class GATEncoder(nn.Module):
    """
    2-layer GAT that produces a 64-dim embedding per drug node.

    Parameters
    ----------
    in_channels : int   – input feature dimension (200 for TF-IDF)
    num_classes : int   – number of severity classes (4)
    hidden      : int   – hidden dim per head in Layer 1 (default 128)
    heads       : int   – number of attention heads in Layer 1 (default 4)
    dropout     : float – dropout probability (default 0.3)
    """

    def __init__(self, in_channels: int, num_classes: int,
                 hidden: int = 128, heads: int = 4, dropout: float = 0.3):
        super().__init__()
        self.dropout = dropout

        # Layer 1: multi-head attention, concat → hidden * heads
        self.gat1 = GATConv(
            in_channels, hidden,
            heads=heads, concat=True, dropout=dropout
        )

        # Layer 2: single-head attention, no concat → 64-dim embedding
        self.gat2 = GATConv(
            hidden * heads, 64,
            heads=1, concat=False, dropout=dropout
        )

        # Classification head (used only during training)
        self.classifier = nn.Linear(64, num_classes)

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Return 64-dim node embeddings (no classification head)."""
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.gat1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.gat2(x, edge_index)
        return x  # shape: (num_nodes, 64)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Full forward pass: node features → class logits."""
        emb = self.encode(x, edge_index)
        return self.classifier(emb)  # shape: (num_nodes, num_classes)
