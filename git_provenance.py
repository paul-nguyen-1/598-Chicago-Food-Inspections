# Simple git tracking for provenance
import subprocess
import json
from datetime import datetime

def track_git_version():
    """Save git info when we run the workflow."""
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        message = subprocess.check_output(['git', 'log', '-1', '--pretty=%s']).decode().strip()
        
        # Save to simple file
        with open('version_info.txt', 'w') as f:
            f.write(f"Workflow run: {datetime.now()}\n")
            f.write(f"Git commit: {commit}\n")
            f.write(f"Commit message: {message}\n")
        
        print(f"Tracked version: {commit[:8]}")
        return commit[:8]
    except:
        print("No git info available")
        return "unknown"

if __name__ == "__main__":
    track_git_version()