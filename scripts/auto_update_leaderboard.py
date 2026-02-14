"""
Automatically update leaderboard from environment variables.
Called by GitHub Actions workflow.
"""

import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Add competition directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "competition"))
from render_leaderboard import main as render_leaderboard

def update_leaderboard():
    """Update leaderboard using environment variables from GitHub Actions"""
    
    # Get data from environment variables
    team = os.environ.get('TEAM')
    run_id = os.environ.get('RUN_ID')
    score = os.environ.get('SCORE')
    model = os.environ.get('MODEL')
    llm_name = os.environ.get('LLM_NAME')
    notes = os.environ.get('NOTES', '')
    
    # Validate required fields
    if not all([team, run_id, score, model]):
        print("❌ Missing required environment variables")
        sys.exit(1)
    
    try:
        score = float(score)
    except ValueError:
        print(f"❌ Invalid score value: {score}")
        sys.exit(1)
    
    print(f"📊 Updating leaderboard:")
    print(f"   Team: {team}")
    print(f"   Run: {run_id}")
    print(f"   Score: {score}")
    print(f"   Model: {model}")
    print(f"   LLM: {llm_name}")
    
    leaderboard_path = Path(__file__).parent.parent / "leaderboard" / "leaderboard.csv"
    
    # Load existing leaderboard or create new
    if leaderboard_path.exists():
        leaderboard = pd.read_csv(leaderboard_path)
    else:
        leaderboard = pd.DataFrame(columns=[
            'timestamp_utc', 'team', 'model', 'score', 'notes'
        ])
    
    # Build notes field
    notes_combined = f"{run_id} | LLM: {llm_name}"
    if notes:
        notes_combined += f" | {notes}"
    
    # Add new entry
    new_entry = {
        'timestamp_utc': datetime.utcnow().isoformat() + 'Z',
        'team': team,
        'model': model,
        'score': score,
        'notes': notes_combined
    }
    
    leaderboard = pd.concat([leaderboard, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save with exact column order
    leaderboard = leaderboard[['timestamp_utc', 'team', 'model', 'score', 'notes']]
    leaderboard.to_csv(leaderboard_path, index=False)
    
    # Render markdown
    render_leaderboard()
    
    print(f"✅ Leaderboard updated successfully!")

if __name__ == '__main__':
    update_leaderboard()