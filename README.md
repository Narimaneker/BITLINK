# BITLINK - Bitcoin Transaction Network

This repository provides a **secure, reproducible template** for running a
Graph Neural Network (GNN) link prediction competition on the **Elliptic Bitcoin Dataset** 
that supports **humans and LLMs** competing on equal footing.

The design intentionally **does not execute participant code**. Instead,
participants submit **predictions only**, which are automatically evaluated
and ranked on a public leaderboard using GitHub Actions.

This makes the competition:
- Safe (no untrusted code execution)
- Fully reproducible
- Suitable for human-vs-LLM evaluation studies

---

## 1. Task Overview

**Task:** Link prediction on Bitcoin transaction graph  
**Dataset:** Elliptic Bitcoin Dataset (from HuggingFace: rexaro/elliptic-bitcoin-dataset)  
**Input:** Public graph structure and node features from Bitcoin transactions  
**Output:** Binary predictions for existence/non-existence of links between node pairs  
**Metric:** Accuracy (binary classification)

Participants train any GNN or non-GNN model *offline* and submit binary predictions
for the test node pairs.

---

## 2. Dataset Information

**Source:** [rexaro/elliptic-bitcoin-dataset](https://huggingface.co/datasets/rexaro/elliptic-bitcoin-dataset) on HuggingFace

The Elliptic Bitcoin Dataset maps Bitcoin transactions to real entities and includes:
- **Nodes:** Bitcoin transactions
- **Edges:** Flow of Bitcoin between transactions
- **Node Features:** Transaction metadata (time step, local features, aggregate features)
- **Task:** Predict whether a link (transaction flow) exists between pairs of nodes

**Data Files:**
- `train_features.csv` / `val_features.csv` / `test_features.csv`: Node feature matrices
- `train_edges.csv` / `val_edges.csv` / `test_edges.csv`: Graph edge lists
- Training and validation data include both positive (existing) and negative (non-existing) link examples
- Test set contains node pairs for which you must predict link existence probability

The dataset has been preprocessed and split into:
- **Training set:** For model training with known link labels
- **Validation set:** For hyperparameter tuning and model selection
- **Test set:** For final evaluation (labels hidden)

---

## 3. Repository Structure

```
.
├── data/
│   ├── public/
│   │   ├── train_features.csv       # Node features for training graph
│   │   ├── train_edges.csv          # Training graph edges
│   │   ├── val_features.csv         # Node features for validation graph
│   │   ├── val_edges.csv            # Validation graph edges
│   │   ├── test_features.csv        # Node features for test graph
│   │   ├── test_edges.csv           # Test graph edges (background)
│   │   └── sample_submission.csv    # Submission format example
│   └── private/
│       └── test_labels.csv          # never committed (used only in CI)
├── competition/
│   ├── config.yaml
│   ├── validate_submission.py
│   ├── evaluate.py
│   └── metrics.py
├── submissions/
│   ├── README.md
│   └── inbox/
├── leaderboard/
│   ├── leaderboard.csv
│   └── leaderboard.md
└── .github/workflows/
    ├── score_submission.yml
    └── publish_leaderboard.yml
```

---

## 4. Submission Format

Participants submit a **single CSV file**:

**predictions.csv**
```
id,y_pred
0,1
1,0
2,1
...
```

Rules:
- `id` is the row index (0, 1, 2, ...) corresponding to test samples
- One row per test sample
- `y_pred` must be either **0** (no link) or **1** (link exists)
- No missing or duplicate IDs
- IDs must be sequential starting from 0

A sample is provided in:
```
data/public/sample_submission.csv
```

---

## 5. How to Submit

1. Fork this repository
2. Create a new folder:
```
submissions/inbox/<team_name>/<run_id>/
```
3. Add:
   - `predictions.csv`
   - `metadata.json`

Example `metadata.json`:
```json
{
  "team": "example_team",
  "model": "llm-only",
  "llm_name": "gpt-x",
  "notes": "Graph attention network for Bitcoin transaction link prediction"
}
```

4. Open a Pull Request to `main`

The PR will be **automatically scored** and the result posted as a comment.

---

## 6. Leaderboard

After a PR is merged, the submission is added to:
- `leaderboard/leaderboard.csv`
- `leaderboard/leaderboard.md`

Rankings are sorted by **descending score**.

---

## 7. Rules

- No external or private data
- No manual labeling of test data
- No modification of evaluation scripts
- Unlimited offline training is allowed
- Only predictions are submitted

Violations may result in disqualification.

---

## 8. Human vs LLM Studies

To use this competition for research:
- Fix a time budget (e.g., 2 hours)
- Fix a submission budget (e.g., 5 runs)
- Record metadata fields (`model`, `llm_name`)
- Compare:
  - validity rate
  - best score within K submissions
  - score vs submission index

---

## 9. Citation

If you use this template or the Elliptic Bitcoin Dataset in academic work, please cite:

**This Competition Template:**
```
[Repository citation - to be added]
```

**Elliptic Bitcoin Dataset:**
```bibtex
@inproceedings{weber2019anti,
  title={Anti-money laundering in bitcoin: Experimenting with graph convolutional networks for financial forensics},
  author={Weber, Mark and Domeniconi, Giacomo and Chen, Jie and Weidele, Daniel Karl I and Bellei, Claudio and Robinson, Tom and Leiserson, Charles E},
  booktitle={Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining},
  pages={1954--1964},
  year={2019}
}

```



---

## 10. License

MIT License.

---

## 11. Interactive Leaderboard (GitHub Pages)

This template includes an interactive leaderboard page inspired by modern benchmark sites.

**Enable GitHub Pages** (Settings → Pages) and set the source to the `main` branch `/docs` folder.
Then open `https://<your-org>.github.io/<repo>/leaderboard.html`.