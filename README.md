# 598-Chicago-Food-Inspections

Integrated dataset for exploring patterns in restaurant inspection failures through data lifecycle processes.

## Quick Start
```bash
pip install -r requirements.txt
python workflow.py
```

## Datasets
- Food Inspections: `food_inspections.csv`
- Business Licenses: `business_licenses.csv` 
- 311 Sanitation Complaints: `311_complaints.csv`

## Output
- `clean_dataset.csv`: Curated integrated dataset
- `data_report.txt`: Quality metrics and statistics
- `provenance.log`: Processing provenance trail

## Validation
Run exploratory analysis:
```bash
python analysis.py
```