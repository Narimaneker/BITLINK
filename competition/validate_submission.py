import pandas as pd
import sys

def main(pred_path, expected_count=None):
    preds = pd.read_csv(pred_path)

    # Check required columns
    if "id" not in preds.columns or "y_pred" not in preds.columns:
        raise ValueError("predictions.csv must contain 'id' and 'y_pred' columns")

    # Check for duplicates
    if preds["id"].duplicated().any():
        raise ValueError("Duplicate IDs found in predictions")

    # Check for missing values
    if preds["y_pred"].isna().any():
        raise ValueError("NaN predictions found")

    # Check prediction range [0, 1]
    if ((preds["y_pred"] < 0) | (preds["y_pred"] > 1)).any():
        raise ValueError("Predictions must be in [0, 1]")

    # Check expected count if provided
    if expected_count is not None:
        if len(preds) != expected_count:
            raise ValueError(f"Expected {expected_count} predictions, got {len(preds)}")
    
    # Check IDs are sequential from 0
    expected_ids = set(range(len(preds)))
    if set(preds["id"]) != expected_ids:
        raise ValueError(f"IDs must be sequential from 0 to {len(preds)-1}")

    print("✅ VALID SUBMISSION")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], int(sys.argv[2]))
    else:
        main(sys.argv[1])