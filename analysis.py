#!/usr/bin/env python3
"""Exploratory analysis for validation."""

import pandas as pd

def main():
    data = pd.read_csv('clean_dataset.csv')
    
    print("=== VALIDATION ANALYSIS ===\n")
    print(f"Total records: {len(data):,}")
    print(f"Date range: {data['inspection_date'].min()} to {data['inspection_date'].max()}\n")
    
    # Most frequent violations
    print("Top 5 Violation Categories:")
    print(data['violation_category'].value_counts().head())
    
    # Results distribution
    print("\nInspection Results:")
    print(data['results'].value_counts())
    overall_fail_rate = data['results'].str.contains('Fail', na=False).mean()
    print(f"Overall failure rate: {overall_fail_rate:.1%}")
    
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
        diff = complaint_failures - no_complaint_failures
        print(f"Failure rate with complaints: {complaint_failures:.1%}")
        print(f"Failure rate without complaints: {no_complaint_failures:.1%}")
        print(f"Difference: {diff:.1%}")
    
    # Risk level analysis
    if 'risk' in data.columns:
        print("\nFailure rate by risk:")
        for risk in data['risk'].dropna().unique():
            risk_data = data[data['risk'] == risk]
            fail_rate = risk_data['results'].str.contains('Fail', na=False).mean()
            print(f"{risk}: {fail_rate:.1%} ({len(risk_data):,} inspections)")
    
    # Trends by year
    print("\nTrends by Year:")
    data['year'] = pd.to_datetime(data['inspection_date']).dt.year
    yearly = data.groupby('year').agg({
        'inspection_id': 'count',
        'results': lambda x: x.str.contains('Fail', na=False).mean()
    }).rename(columns={'inspection_id': 'inspections', 'results': 'failure_rate'})
    print(yearly.to_string())
    
    # Facility types
    print("\nTop Facility Types by Failure Rate:")
    facility_fails = data.groupby('facility_type').agg({
        'inspection_id': 'count',
        'results': lambda x: x.str.contains('Fail', na=False).mean()
    }).rename(columns={'inspection_id': 'count', 'results': 'fail_rate'})
    facility_fails = facility_fails[facility_fails['count'] >= 10]
    print(facility_fails.sort_values('fail_rate', ascending=False).head(10).to_string())
    
    # Analysis_summary.txt
    with open('analysis_summary.txt', 'w') as f:
        f.write(f"Chicago Food Inspections Analysis Summary - {pd.Timestamp.now()}\n\n")
        f.write(f"Total Records: {len(data):,}\n")
        f.write(f"Date Range: {data['inspection_date'].min()} to {data['inspection_date'].max()}\n")
        f.write(f"Overall Failure Rate: {overall_fail_rate:.1%}\n")
        f.write(f"Locations with Complaints: {(data['complaint_count'] > 0).sum():,}\n\n")
        f.write("Key Findings:\n")
        f.write(f"1. Most common violation: {data['violation_category'].value_counts().index[0]}\n")
        if data['complaint_count'].sum() > 0:
            f.write(f"2. Locations with complaints have {diff:.1%} higher failure rate\n")
        f.write(f"3. Total unique facilities: {data['license_number'].nunique():,}\n")
    
    print(f"\nAnalysis complete. Summary saved to analysis_summary.txt")

if __name__ == "__main__":
    main()
