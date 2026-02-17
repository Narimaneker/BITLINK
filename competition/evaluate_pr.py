"""
Wrapper script for evaluating submissions in GitHub Actions.
Uses the existing evaluate.py and validate_submission.py scripts.
"""

import pandas as pd
import json
import os
import glob
import sys
from pathlib import Path

# Add competition directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validate_submission import main as validate
from evaluate import main as evaluate_main
from metrics import binary_auc

def find_submission_files():
    """Find submission files - one submission per team, no run_id folder"""
    # Pattern: submissions/inbox/TEAM_NAME/predictions.csv
    pred_pattern = "submissions/inbox/*/predictions.csv"
    meta_pattern = "submissions/inbox/*/metadata.json"

    pred_files = glob.glob(pred_pattern)
    meta_files = glob.glob(meta_pattern)

    if not pred_files:
        raise FileNotFoundError(
            "No predictions.csv found in submissions/inbox/TEAM_NAME/. "
            "Make sure the decrypted file was copied to the correct path."
        )
    if not meta_files:
        raise FileNotFoundError(
            "No metadata.json found in submissions/inbox/TEAM_NAME/."
        )

    if len(pred_files) > 1:
        raise ValueError(f"Multiple prediction files found: {pred_files}. Submit only one.")

    return pred_files[0], meta_files[0]


def load_metadata(metadata_path):
    """Load and validate metadata — no run_id required"""
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # run_id removed — one submission per team
    required_fields = ['team', 'model']
    missing = [f for f in required_fields if f not in metadata]
    if missing:
        raise ValueError(f"Missing required metadata fields: {missing}")

    return metadata


def run_evaluation():
    """Main evaluation function"""
    try:
        # Check if test labels exist (decoded from GitHub Secret)
        if not os.path.exists('test_labels.csv'):
            raise FileNotFoundError(
                "test_labels.csv not found. "
                "GitHub Secret TEST_LABELS_CSV may not be properly configured."
            )

        # Load test labels
        test_labels = pd.read_csv('test_labels.csv')
        expected_count = len(test_labels)
        print(f"📋 Test labels loaded: {expected_count} entries")

        # Find submission files
        pred_path, meta_path = find_submission_files()

        # Load metadata
        metadata = load_metadata(meta_path)

        # Extract team from folder path
        team = Path(pred_path).parent.name

        print(f"📁 Found submission: {pred_path}")
        print(f"👥 Team: {team}")

        # Validate submission format
        print("\n🔍 Validating submission format...")
        try:
            validate(pred_path, expected_count)
        except Exception as e:
            raise ValueError(f"Validation failed: {str(e)}")

        # Evaluate predictions
        print("\n📊 Evaluating predictions...")
        predictions = pd.read_csv(pred_path).sort_values("id")
        labels = test_labels.sort_values("id")

        # Merge and check
        merged = labels.merge(predictions, on="id", how="inner")
        if len(merged) != len(labels):
            raise ValueError(
                f"ID mismatch: expected {len(labels)} predictions, "
                f"got {len(merged)} matching IDs."
            )

        # Calculate ROC-AUC
        roc_auc = binary_auc(merged["label"], merged["y_pred"])

        # Calculate accuracy
        binary_pred = (merged["y_pred"] >= 0.5).astype(int)
        accuracy = (binary_pred == merged["label"]).mean()

        # Prepare result
        result = {
            'team': team,
            'run_id': 'run_001',
            'model': metadata.get('model', 'unknown'),
            'llm_name': metadata.get('llm_name', 'none'),
            'roc_auc': float(roc_auc),
            'accuracy': float(accuracy),
            'notes': metadata.get('notes', ''),
            'valid': True,
            'errors': None,
            'submission_path': pred_path
        }

        print(f"\n✅ Evaluation successful!")
        print(f"   ROC-AUC:  {roc_auc:.4f}")
        print(f"   Accuracy: {accuracy:.4f}")

    except Exception as e:
        result = {
            'team': 'unknown',
            'run_id': 'unknown',
            'model': 'unknown',
            'llm_name': 'none',
            'roc_auc': 0.0,
            'accuracy': 0.0,
            'notes': '',
            'valid': False,
            'errors': str(e),
            'submission_path': None
        }
        print(f"\n❌ Evaluation failed: {str(e)}")

    # Save result for GitHub Actions
    with open('evaluation_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == '__main__':
    run_evaluation()