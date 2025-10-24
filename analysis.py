#!/usr/bin/env python3
"""Exploratory analysis for validation."""

import pandas as pd

def main():
    data = pd.read_csv('clean_dataset.csv')
    
    print("=== VALIDATION ANALYSIS ===\n")
    
    # Most frequent violations
    print("Top 5 Violation Categories:")
    print(data['violation_category'].value_counts().head())
    
    # Failure rate by license status
    if 'license_status' in data.columns:
        print("\nFailure Rate by License Status:")
        failures = data[data['results'].str.contains('Fail', na=False)]
        rate = failures.groupby('license_status').size() / data.groupby('license_status').size()
        print(rate.sort_values(ascending=False))
    
    # Complaint correlation
    print(f"\nLocations with complaints: {(data['complaint_count'] > 0).sum():,}")
    if data['complaint_count'].sum() > 0:
        complaint_failures = data[data['complaint_count'] > 0]['results'].str.contains('Fail', na=False).mean()
        no_complaint_failures = data[data['complaint_count'] == 0]['results'].str.contains('Fail', na=False).mean()
        print(f"Failure rate with complaints: {complaint_failures:.1%}")
        print(f"Failure rate without complaints: {no_complaint_failures:.1%}")

if __name__ == "__main__":
    main()