import torch
import torch.nn as nn
from torch_geometric.nn import GATConv

class DrugInteractionGAT(nn.Module):
    """
    Standard GAT Backbone for modeling structural drug relationships.
    Captures topological importance weights between drug nodes.
    """
    def __init__(self, in_channels, hidden_channels, out_channels, heads=4):
        super(DrugInteractionGAT, self).__init__()
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads)
        self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = self.conv2(x, edge_index)
        return x

class SemanticFusionNet(nn.Module):
    """
    Core Fusion Layer: Concatenates GAT structural features with SciBERT semantic vectors.
    """
    def __init__(self, structural_dim, semantic_dim, num_classes=4):
        super(SemanticFusionNet, self).__init__()
        self.fusion = nn.Sequential(
            nn.Linear(structural_dim + semantic_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def forward(self, structural_v, semantic_v):
        combined = torch.cat((structural_v, semantic_v), dim=1)
        return self.fusion(combined)
