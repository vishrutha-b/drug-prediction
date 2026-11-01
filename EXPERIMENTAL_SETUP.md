# ⚗️ Experimental Setup

## 4.1 Environment Configuration

All experiments were conducted using **Python 3.12** on a Windows/Linux cross-platform environment. The deep learning components were implemented using **PyTorch** and **PyTorch Geometric**, while the gradient boosting ensemble utilized **XGBoost** and **CatBoost** libraries. Feature extraction relied on **Scikit-learn's TF-IDF vectorizer**. The complete backend was served via **FastAPI with Uvicorn**, and the full platform was containerized using **Docker (multi-stage build)**.

| Component | Library / Version |
|---|---|
| Programming Language | Python 3.12 |
| Deep Learning | PyTorch + PyTorch Geometric (GATConv) |
| Gradient Boosting | XGBoost, CatBoost |
| Feature Extraction | Scikit-learn (TF-IDF) |
| Data Processing | Pandas, NumPy |
| Backend Framework | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy 2.0 |
| Containerization | Docker (Multi-stage) |

---

## 4.2 Dataset Preparation

The dataset was sourced from the **FDA Adverse Event Reporting System (FAERS)** via the openFDA public API (`https://api.fda.gov/drug/event.json`). A total of **8,000 serious adverse event reports** were collected (80 pages × 100 reports per page). From these reports, all drug-pair combinations were extracted and aggregated to produce **75,537 unique canonical drug-drug interaction pairs**, covering over **14,000 distinct drug compounds**.

Each pair was labeled with a **severity class** derived from FDA outcome codes as follows:

| FDA Outcome Code | Severity Label Assigned |
|---|---|
| DE (Death), LT (Life-Threatening) | DEATH RISK |
| HO (Hospitalization), DS (Disability) | HOSPITAL ADMISSION |
| CA (Congenital Anomaly), RI (Intervention Required), OT (Other) | MONITORING REQUIRED |
| No serious outcome | SAFE |

When a drug pair appeared in multiple reports with differing outcomes, the **worst-case severity** was retained to prioritize patient safety.

---

## 4.3 Data Preprocessing

Before training, the raw dataset was cleaned through the following steps:

1. **Name Normalization** — All drug names were converted to uppercase and stripped of whitespace.
2. **Validation** — Rows with drug names of length ≤ 1 or unrecognized severity labels were removed.
3. **Canonical Deduplication** — Drug pairs (A, B) and (B, A) were treated as identical by sorting both names before comparison. Duplicate pairs retained the highest severity label.
4. **Missing Value Imputation** — Missing `report_count` values were filled with 1.0.

The cleaned dataset was saved as `ml/data/faers_pairs_clean.csv` for all subsequent experiments.

---

## 4.4 Train / Test Split

The dataset was divided into training and testing sets using an **80/20 stratified split**, maintaining class proportions across both sets. A **fixed random seed of 42** was used throughout all experiments to ensure full reproducibility.

| Split | Proportion | Method |
|---|---|---|
| Training Set | 80% | Stratified split (`stratify=y`, seed=42) |
| Test Set | 20% | Held-out for final evaluation only |

For the **GAT model**, the split was applied at the **node level** (drug nodes), with 80% of nodes forming the training mask and 20% the validation mask, using `torch.Generator().manual_seed(42)`.

---

## 4.5 Feature Extraction

### Semantic Embeddings (TF-IDF Character N-Grams)

A **TF-IDF vectorizer** with character-level n-grams (analyzer=`char_wb`, n-gram range 3–5) was fitted on all unique drug names in the training set, producing a **200-dimensional embedding** per drug name. Character n-grams were chosen because they capture morphological patterns in drug names that correlate with pharmacological class (e.g., `-statin` for HMG-CoA inhibitors, `-pril` for ACE inhibitors).

### Graph-Based Embeddings (GAT Node Embeddings)

The interaction dataset was modeled as an **undirected pharmacological graph**:
- **Nodes** — Unique drug compounds (~14,000+), each initialized with its 200-dim TF-IDF embedding
- **Edges** — FAERS-documented drug pairs (bidirectional)

A **2-layer Graph Attention Network (GAT)** was trained on this graph to produce **64-dimensional latent embeddings** per drug node that encode its pharmacological interaction neighborhood.

### Final Feature Vector (133-Dimensional)

For the ensemble classifier, each drug pair was encoded as a **133-dimensional feature vector**:

| Feature | Dimensions | Description |
|---|---|---|
| GAT embedding of Drug A | 64 | Learned 64-dim node embedding |
| GAT embedding of Drug B | 64 | Learned 64-dim node embedding |
| log(1 + report_count) | 1 | Log-scaled FAERS evidence count |
| Pair hash (normalized MD5) | 1 | Canonical pair identifier |
| Name length of Drug A | 1 | Character count |
| Name length of Drug B | 1 | Character count |
| Sum of name lengths | 1 | Combined length |
| Absolute length difference | 1 | Length asymmetry |
| **Total** | **133** | |

For drugs not present in the GAT embedding dictionary (novel compounds), the first 64 dimensions of the TF-IDF embedding were used as a fallback (`TF-IDF[:64]`).

---

## 4.6 Model Configuration

### Graph Attention Network (GAT)

The GAT model consists of **two GATConv layers** with the following configuration:

| Layer | Input Dim | Hidden Dim | Heads | Output Dim | Activation |
|---|---|---|---|---|---|
| GATConv Layer 1 | 200 | 128 | 4 (concat) | 512 | ELU |
| GATConv Layer 2 | 512 | — | 1 (no concat) | 64 | — |
| Classification Head | 64 | — | — | 4 classes | Softmax |

The 64-dimensional output of Layer 2 served as the drug node embedding for downstream use. The classification head was used only during training.

**GAT Training Hyperparameters:**

| Hyperparameter | Value |
|---|---|
| Optimizer | Adam |
| Learning Rate | 0.005 |
| Weight Decay (L2) | 5 × 10⁻⁴ |
| Dropout | 0.3 |
| Max Epochs | 200 |
| Early Stopping Patience | 20 epochs |
| Loss Function | Weighted Cross-Entropy |
| Random Seed | 42 |

### Class Imbalance Handling

Inverse-frequency class weights were computed on the training nodes to address class imbalance in the FAERS dataset:

```
class_weight[c] = total_samples / (num_classes × count[c] + ε)
```

This ensured that rare but clinically critical classes (e.g., `DEATH RISK`) received proportionally higher loss contributions during training.

### XGBoost Classifier

| Hyperparameter | Value |
|---|---|
| Number of Estimators | 400 |
| Max Tree Depth | 6 |
| Learning Rate | 0.05 |
| Subsample | 0.8 |
| Column Sample by Tree | 0.8 |
| Evaluation Metric | mlogloss |
| Random State | 42 |

### CatBoost Classifier

| Hyperparameter | Value |
|---|---|
| Iterations | 400 |
| Tree Depth | 6 |
| Learning Rate | 0.05 |
| Evaluation Metric | Accuracy |
| Random Seed | 42 |

---

## 4.7 Ensemble Strategy

Both classifiers were trained independently on the same 80% training split. At inference time, their predicted **class probability distributions** were combined using **equal-weight soft-voting**:

```
P_final(c) = 0.5 × P_XGBoost(c)  +  0.5 × P_CatBoost(c)

Predicted class = argmax  P_final(c)
                     c
```

Soft-voting was preferred over hard-voting because it preserves uncertainty information across all severity classes, enabling the system to report per-class confidence scores alongside the final prediction.

---

## 4.8 Evaluation Metrics

The following metrics were used to evaluate model performance on the held-out 20% test set:

| Metric | Formula | Rationale |
|---|---|---|
| **Recall (per class)** | TP / (TP + FN) | Primary metric — critical for safety-sensitive classification; missing a DEATH RISK interaction is unacceptable |
| **Precision (per class)** | TP / (TP + FP) | Measures clinical credibility; excessive false positives reduce clinician trust |
| **F1-Score (per class)** | 2 × P × R / (P + R) | Harmonic mean balancing precision and recall |
| **Overall Accuracy** | Correct / Total | General performance measure on the stratified test set |

> **Priority:** Recall on `DEATH RISK` was designated the **primary evaluation metric** due to the safety-critical nature of the classification task. A false negative on this class (a missed fatal interaction) carries far greater clinical risk than a false positive.

---

## 4.9 Reproducibility

To ensure that all reported results are fully reproducible, the following fixed random seeds were applied:

| Component | Seed Setting |
|---|---|
| GAT node mask split | `torch.Generator().manual_seed(42)` |
| Ensemble train/test split | `random_state=42` in `train_test_split` |
| XGBoost training | `random_state=42` |
| CatBoost training | `random_seed=42` |

The full training pipeline can be reproduced with a single command:

```bash
cd "drug prediction"
python ml/pipeline/run_full_pipeline.py
```

---

## 4.10 Three-Tier Inference Design

Beyond offline training evaluation, the deployed system implements a **three-tier inference cascade** to guarantee 100% availability in production:

| Tier | Mechanism | Activated When |
|---|---|---|
| **Tier 1** | Exact lookup against all 75,537 FAERS pairs | Drug pair found in FAERS dictionary |
| **Tier 2** | GAT embeddings + XGBoost/CatBoost soft-vote | Novel pair; ensemble models available |
| **Tier 3** | Deterministic rule-based simulation | No trained model files present |

This cascade ensures the system returns a prediction for **every possible drug pair** under all deployment conditions, including environments where model training has not yet been completed.

---

*Part of the **IntelliInteraction — Precision Drug-Drug Interaction Safety Platform** project report.*
