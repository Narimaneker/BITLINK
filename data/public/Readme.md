# 🪙 Bitcoin Transaction Graph – Edge Prediction Challenge

This repository contains a modified version of the Elliptic Bitcoin Transaction Dataset, adapted for a **temporal edge prediction task**.

The goal of the challenge is to predict whether a directed edge exists between two Bitcoin transactions.

---

# 📦 Dataset Description

The dataset is derived from the Elliptic Bitcoin Transaction Dataset, which represents Bitcoin transactions as a directed graph.

Each node corresponds to a Bitcoin transaction, and each directed edge represents a flow of Bitcoin between transactions (i.e., one transaction spends outputs from another).

The original dataset contains three CSV files:

---

## 1️⃣ elliptic_txs_features.csv

This file contains transaction-level features.

- **166 features per transaction**
  - 94 local features  
  - 72 aggregated features  

For this competition version:

✅ Only the **first 7 local features** were retained.  
❌ All remaining local and aggregated features were removed.

This significantly increases task difficulty by limiting node information.

---

## 2️⃣ elliptic_txs_classes.csv

This file contains transaction labels:

- `1` → Illicit  
- `2` → Licit  
- `unknown` → Unlabeled transactions  

(Note: Class labels are not directly used in the edge prediction task.)

---

## 3️⃣ elliptic_txs_edgelist.csv

This file defines the directed transaction graph.

- Each row represents a directed edge.
- An edge from transaction **X → Y** means:
  - Transaction Y spends outputs created by transaction X.
- The graph is directed and acyclic.

---

# 📊 Dataset Statistics (Original)

- **Total transactions:** 203,769  
- **Illicit transactions:** ~4,545  
- **Licit transactions:** ~42,019  
- **Unlabeled transactions:** ~157,205  
- **Total time steps:** 49  

---

# 🔄 Transformations Applied for the Competition

This competition version introduces controlled modifications to increase realism and difficulty.

---

## 🕒 1. Temporal Splitting

The dataset was split chronologically to prevent future leakage:

- **Training set:** Time steps ≤ 15  
- **Validation set:** Time step 20  
- **Test set:** Time step 24  

This enforces strict temporal generalization.

---

## 🧹 2. Node Feature Reduction

Only the **first 7 local features** were retained.

This forces models to rely more on structural learning rather than rich feature representations.

---

## 🕸 3. Graph Sparsity

To simulate incomplete blockchain observations:

- Only **80% of the original training edges were retained**
- 20% were randomly removed

Sparsity was applied **only to the training graph**.

Validation and test graphs were kept intact for evaluation integrity.

---

## ➖ 4. Negative Sampling

For the edge prediction task:

- Positive edges = real transaction flows
- Negative edges = randomly sampled non-existing transaction pairs

Negative samples were generated separately for:
- Training set
- Validation set
- Test set

---

## ⚖️ 5. Imbalanced Test Set

To reflect real-world graph sparsity, the test set is intentionally imbalanced:

- **990 positive edges**
- **2500 negative edges**

Total test edges: **3490**

This makes the task more realistic and prevents trivial classifiers.

---

# 🎯 Task Definition

Participants must:

> Predict whether a directed edge exists between two transactions in the test set.

Each submission file must contain:

- `id`
- `y_pred` (probability or score of edge existence)

Evaluation metric: **AUC**

---

# 🧠 Why This Challenge Is Difficult

- Very limited node features (only 7)
- Sparse training graph (20% edges removed)
- Temporal split (no future information)
- Imbalanced test set
- Directed financial transaction network

This setup mimics real-world blockchain link prediction scenarios.
