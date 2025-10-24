# How to Track Your Work

## Basic Git Setup
```bash
git init
git add .
git commit -m "Initial data processing setup"
```

## Before Running Workflow
```bash
# Save your changes
git add .
git commit -m "Updated cleaning logic"

# Run the workflow
python workflow.py
```

## What Gets Tracked
- Git commit used for each run (in version_info.txt)
- Processing steps (in provenance.log)
- When workflow was run

## To See What Happened
```bash
python provenance_viewer.py
```

## To Reproduce Results
```bash
# Find the commit
git log --oneline

# Go back to that version
git checkout abc1234

# Run again
python workflow.py
```