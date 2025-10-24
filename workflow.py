import pandas as pd
import logging
import subprocess
from datetime import datetime

# Simple logging setup
logging.basicConfig(
    filename='provenance.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_step(step, details=""):
    """Log what we're doing for provenance."""
    message = f"{step}: {details}" if details else step
    logging.info(message)
    print(f"✓ {message}")

def get_git_commit():
    """Get current git commit for tracking."""
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()[:8]
        return commit
    except:
        return "no-git"

def main():
    print("Starting data processing workflow...")
    
    # Track git version
    from git_provenance import track_git_version
    commit = track_git_version()
    log_step("WORKFLOW_START", f"Git commit: {commit}")
    
    # Run the data processing
    log_step("PROCESSING", "Running data cleaning and integration")
    exec(open('main.py').read())
    
    # Check results
    try:
        result_data = pd.read_csv('clean_dataset.csv')
        log_step("COMPLETE", f"Generated {len(result_data)} records")
        print(f"Done! Created clean_dataset.csv with {len(result_data):,} records")
    except:
        log_step("ERROR", "Failed to create output file")

if __name__ == "__main__":
    main()