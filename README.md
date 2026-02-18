# BITLINK - Bitcoin Transaction Network

This repository provides a **secure, reproducible template** for running a
Graph Neural Network (GNN) link prediction competition on the **Elliptic Bitcoin Dataset**
that supports **humans and LLMs** competing on equal footing.

The design intentionally **does not execute participant code**. Instead,
participants submit **encrypted predictions only**, which are automatically decrypted,
evaluated, and ranked on a public leaderboard using GitHub Actions.

This makes the competition:
- 🔒 **Secure** — predictions are encrypted, test labels are never exposed
- ⚙️ **Fully automated** — no manual intervention required
- ⚖️ **Fair** — suitable for human-vs-LLM evaluation studies

---

## 1. Task Overview

**Task:** Link prediction on Bitcoin transaction graph  
**Dataset:** Elliptic Bitcoin Dataset (from HuggingFace: rexaro/elliptic-bitcoin-dataset)  
**Input:** Public graph structure and node features from Bitcoin transactions  
**Output:** Probability predictions (0.0 to 1.0) for existence of links between node pairs  
**Metric:** ROC-AUC  

Participants train any GNN or non-GNN model *offline* and submit **encrypted probability predictions**
for the test node pairs.

---

## 2. Dataset Information

**Source:** [rexaro/elliptic-bitcoin-dataset](https://huggingface.co/datasets/rexaro/elliptic-bitcoin-dataset) on HuggingFace

The Elliptic Bitcoin Dataset maps Bitcoin transactions to real entities and includes:
- **Nodes:** Bitcoin transactions
- **Edges:** Flow of Bitcoin between transactions
- **Node Features:** Only first 7 local features retained (out of 166 original)
- **Task:** Predict whether a link (transaction flow) exists between pairs of nodes

**Splits:**
- **Training set:** Time steps ≤ 15 — for model training with known labels
- **Validation set:** Time step 20 — for hyperparameter tuning
- **Test set:** Time step 24 — for final evaluation (labels hidden)

**Test Set Composition:** 3,490 node pairs — 990 positive edges (28%), 2,500 negative edges (72%)

---

## 3. Repository Structure

```
.
├── data/
│   └── public/
│       ├── train/
│       │   ├── train_features.csv       # Node features for training graph
│       │   └── train_edges.csv          # Training graph edges with labels
│       ├── val/
│       │   ├── val_features.csv         # Node features for validation graph
│       │   └── val_edges.csv            # Validation graph edges with labels
│       └── test/
│           ├── test_features.csv        # Node features for test graph
│           └── test_edges.csv           # Test node pairs (no labels)
├── competition/
│   ├── config.yaml
│   ├── evaluate_pr.py
│   ├── validate_submission.py
│   ├── evaluate.py
│   └── metrics.py
├── encryption/
│   ├── encrypt.py                       # Participants use this to encrypt
│   ├── decrypt.py                       # Used by GitHub Actions only
│   └── public_key.pem                   # Public key for encryption
├── scripts/
│   └── auto_update_leaderboard.py
├── submissions/
│   ├── sample_submission.csv            # Example predictions format
│   └── inbox/                           # One folder per team
│       └── YOUR_TEAM_NAME/
│           ├── predictions.csv.enc      # Encrypted predictions
│           ├── metadata.json            # Team info
│           └── score.txt                # Auto-written after evaluation
├── leaderboard/
│   ├── leaderboard.csv
│   └── leaderboard.md
├── .github/
│   └── workflows/
│       └── evaluate_encrypted_submission.yml
├── .gitattributes
├── .gitignore
└── README.md
```

---

## 4. Submission Format

Generate predictions and save as `predictions.csv`:

```csv
id,y_pred
0,0.92
1,0.13
2,0.78
...
```

**Rules:**
- `id`: Sequential integers from 0 to 3489
- `y_pred`: Probability between **0.0 and 1.0** (not binary!)
- No missing or duplicate IDs
- Exactly 3,490 predictions required

See `submissions/sample_submission.csv` for a complete example.

---

## 5. How to Submit

### Step 1 — Install dependency
```bash
pip install cryptography
```

### Step 2 — Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/BITLINK.git
cd BITLINK
```

### Step 3 — Create your submission folder
```bash
mkdir -p submissions/inbox/YOUR_TEAM_NAME
```

### Step 4 — Encrypt your predictions
```bash
python encryption/encrypt.py \
    predictions.csv \
    encryption/public_key.pem \
    submissions/inbox/YOUR_TEAM_NAME/predictions.csv.enc
```

### Step 5 — Create metadata.json
Save to `submissions/inbox/YOUR_TEAM_NAME/metadata.json`:
```json
{
  "team": "YOUR_TEAM_NAME",
  "model": "gnn",
  "llm_name": "none",
  "notes": "Brief description of your approach"
}
```

**Supported model values:** `gnn`, `llm`, `hybrid`, `baseline`  
**Supported llm_name values:** `none`, `gpt-4`, `gpt-3.5-turbo`, `claude-3-opus`, `claude-3-sonnet`, etc.

### Step 6 — Push and open a Pull Request
```bash
git checkout -b YOUR_TEAM_NAME
git add submissions/inbox/YOUR_TEAM_NAME/
git commit -m "Submission: YOUR_TEAM_NAME"
git push origin YOUR_TEAM_NAME
```
⚠️ Important: Delete predictions.csv before committing! 
Only the encrypted .enc file should be submitted.

#### Windows:
del submissions\inbox\YOUR_TEAM_NAME\predictions.csv

#### Mac/Linux:
rm submissions/inbox/YOUR_TEAM_NAME/predictions.csv
Then go to GitHub → open a **Pull Request** from your fork to the main repository.

> 

### Step 7 — Check your score
After **2-5 minutes**, a `score.txt` is automatically written to your submission folder:
```
submissions/inbox/YOUR_TEAM_NAME/score.txt
```

```
╔══════════════════════════════════════╗
║     BITLINK Evaluation Result        ║
╠══════════════════════════════════════╣
║ Team   : YOUR_TEAM_NAME
║ Score  : 0.8756 (ROC-AUC)
║ Status : Valid
╚══════════════════════════════════════╝
Your score has been added to the leaderboard!
```

> The PR will be **automatically closed** after evaluation. You do not need to do anything else.

---

## 6. Leaderboard

Scores are added automatically after each valid submission:
- `leaderboard/leaderboard.csv` — raw scores database
- `leaderboard/leaderboard.md` — formatted public rankings

Rankings are sorted by **descending ROC-AUC score**.

**One submission per team.** Each team name must be unique.

---

## 7. Security

This competition uses **RSA hybrid encryption** to keep predictions private:

```
Your Machine                      GitHub Actions (Private)
──────────────                    ────────────────────────
predictions.csv
    ↓ encrypt with public_key.pem
predictions.csv.enc ── push ───►  decrypt with private key (GitHub Secret)
(unreadable!)                          ↓ evaluate vs hidden test labels
                                       ↓ delete predictions immediately
                                  score → leaderboard ✅
```

- ✅ Test labels stored as GitHub Secrets — never in the repository
- ✅ Private key stored as GitHub Secrets — never exposed
- ✅ Predictions decrypted only in GitHub Actions — deleted after evaluation
- ✅ No code execution — predictions only
- ✅ Evaluation scripts fetched from `main` branch — cannot be tampered with

---

## 8. Rules

- No external or private data
- No manual labeling of test data
- No modification of evaluation or encryption scripts
- Unlimited offline training is allowed
- Only encrypted predictions are submitted

Violations may result in disqualification.

---

## 9. Human vs LLM Studies

To use this competition for research:
- Fix a time budget (e.g., 2 hours)
- Fix a submission budget (e.g., 5 runs)
- Record metadata fields (`model`, `llm_name`)
- Compare:
  - validity rate
  - best score within K submissions
  - score vs submission index

---

## 10. Citation

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

## 11. License

MIT License.