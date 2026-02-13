"""
Manually update leaderboard after approving a submission.
Reads score from PR evaluation and updates leaderboard.csv
"""

import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path

# Import the existing render function
sys.path.insert(0, str(Path(__file__).parent.parent / "competition"))
from render_leaderboard import main as render_leaderboard

def update_leaderboard(team, run_id, roc_auc, model, llm_name, notes=""):
    """
    Manually add an entry to the leaderboard.
    
    Usage:
      python scripts/update_leaderboard_from_pr.py <team> <run_id> <score> <model> <llm>
    """
    
    leaderboard_path = Path(__file__).parent.parent / "leaderboard" / "leaderboard.csv"
    
    # Load existing leaderboard or create new
    if leaderboard_path.exists():
        leaderboard = pd.read_csv(leaderboard_path)
    else:
        leaderboard = pd.DataFrame(columns=[
            'timestamp_utc', 'team', 'model', 'score', 'notes'
        ])
    
    # Build notes field combining run_id, llm_name, and optional notes
    notes_combined = f"{run_id} | LLM: {llm_name}"
    if notes:
        notes_combined += f" | {notes}"
    
    # Add new entry with exact column order
    new_entry = {
        'timestamp_utc': datetime.utcnow().isoformat() + 'Z',
        'team': team,
        'model': model,
        'score': roc_auc,
        'notes': notes_combined
    }
    
    leaderboard = pd.concat([leaderboard, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save with exact column order
    leaderboard = leaderboard[['timestamp_utc', 'team', 'model', 'score', 'notes']]
    leaderboard.to_csv(leaderboard_path, index=False)
    
    # Render markdown using existing script
    render_leaderboard()
    
    print(f"✅ Added {team}/{run_id} to leaderboard")
    print(f"   Score: {roc_auc:.4f}")
    print(f"   Leaderboard updated and rendered to markdown")

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python update_leaderboard_from_pr.py <team> <run_id> <roc_auc> <model> <llm_name> [notes]")
        print("Example: python update_leaderboard_from_pr.py alice_team run_001 0.8756 gnn none 'My great model'")
        sys.exit(1)
    
    team = sys.argv[1]
    run_id = sys.argv[2]
    roc_auc = float(sys.argv[3])
    model = sys.argv[4]
    llm_name = sys.argv[5] if len(sys.argv) > 5 else "none"
    notes = sys.argv[6] if len(sys.argv) > 6 else ""
    
    update_leaderboard(team, run_id, roc_auc, model, llm_name, notes)