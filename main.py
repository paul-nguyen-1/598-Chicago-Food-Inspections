import pandas as pd

OPTIONAL_LICENSE_FIELDS = [
    'LICENSE STATUS', 'APPLICATION CREATED DATE', 'DATE ISSUED',
    'LICENSE TERM START DATE', 'LICENSE TERM EXPIRATION DATE',
    'LICENSE APPROVED FOR ISSUANCE', 'PAYMENT DATE',
    'CONDITIONAL APPROVAL', 'APPLICATION TYPE'
]

ADDRESS_ABBR = {
    'STREET': 'ST', 'AVENUE': 'AVE', 'ROAD': 'RD', 'DRIVE': 'DR',
    'BOULEVARD': 'BLVD', 'COURT': 'CT', 'PLACE': 'PL', 'LANE': 'LN',
    'NORTH': 'N', 'SOUTH': 'S', 'EAST': 'E', 'WEST': 'W'
}

VIOLATION_KEYWORDS = {
    'Pest Control': ['pest', 'rodent', 'mice', 'rat', 'roach', 'fly'],
    'Sanitation': ['clean', 'sanitary', 'wash', 'dirty', 'hygiene'],
    'Food Storage': ['storage', 'temperature', 'refrigerate', 'freeze'],
    'Food Handling': ['handling', 'preparation', 'cross-contamination', 'raw'],
    'Facility Maintenance': ['floor', 'wall', 'ceiling', 'plumb', 'repair'],
    'License/Permit': ['license', 'permit', 'certified', 'certificate']
}

def find_col(df, *keywords):
    for col in df.columns:
        if all(word.upper() in col.upper() for word in keywords):
            return col
    return None

def clean_address(series):
    cleaned = series.fillna('').astype(str).str.strip().str.upper()
    cleaned = cleaned.str.replace(r'\s+', ' ', regex=True)
    for old, new in ADDRESS_ABBR.items():
        cleaned = cleaned.str.replace(old, new, regex=False)
    return cleaned.replace('', pd.NA)

def clean_id_col(series):
    return series.astype(str).str.strip().str.replace('.0', '', regex=False)

def categorize_violation(text):
    if pd.isna(text):
        return 'Unknown'
    text = str(text).lower()
    for category, keywords in VIOLATION_KEYWORDS.items():
        if any(word in text for word in keywords):
            return category
    return 'Other'

print("Loading data")
inspections = pd.read_csv('food_inspections.csv')
licenses = pd.read_csv('business_licenses.csv')
complaints = pd.read_csv('311_complaints.csv')

print(f"Loaded: {len(inspections):,} inspections, {len(licenses):,} licenses, {len(complaints):,} complaints\n")

inspections['Inspection Date'] = pd.to_datetime(inspections['Inspection Date'], errors='coerce')
inspections['City'] = inspections['City'].str.strip().str.upper()
inspections['Address'] = clean_address(inspections['Address'])
inspections['License #'] = clean_id_col(inspections['License #'])
inspections['Zip'] = clean_id_col(inspections['Zip']).str.zfill(5)
inspections['Violation Category'] = inspections['Violations'].apply(categorize_violation)
inspections['Results'] = inspections['Results'].fillna('Other')

duplicate_inspections = inspections.duplicated(subset=['Inspection ID']).sum()
inspections = inspections.drop_duplicates(subset=['Inspection ID'], keep='first')

license_num_col = find_col(licenses, 'LICENSE', 'NUMBER') or 'LICENSE NUMBER'
licenses['License #'] = clean_id_col(licenses[license_num_col])

address_col = find_col(licenses, 'ADDRESS')
if address_col:
    licenses['Address'] = clean_address(licenses[address_col])

duplicate_licenses = licenses.duplicated(subset=[license_num_col]).sum()
licenses = licenses.drop_duplicates(subset=[license_num_col], keep='first')

complaints['Address'] = clean_address(complaints['Street Address'])
complaints['Creation Date'] = pd.to_datetime(complaints['Creation Date'], errors='coerce')

complaint_stats = complaints.groupby('Address').agg(
    complaint_count=('Service Request Number', 'count'),
    last_complaint=('Creation Date', 'max')
).reset_index()

license_cols = ['License #']
desc_col = find_col(licenses, 'LICENSE', 'DESCRIPTION')
if desc_col:
    license_cols.append(desc_col)
license_cols.extend([f for f in OPTIONAL_LICENSE_FIELDS if f in licenses.columns])

data = inspections.merge(licenses[license_cols], on='License #', how='left')
data = data.merge(complaint_stats, on='Address', how='left')

data['complaint_count'] = data['complaint_count'].fillna(0).astype(int)
days_diff = (data['Inspection Date'] - data['last_complaint']).dt.days
data['days_since_complaint'] = days_diff.astype('Int64').astype(str).replace('<NA>', '')

core_cols = ['Inspection ID', 'DBA Name', 'License #', 'Facility Type']
if desc_col:
    core_cols.append(desc_col)
core_cols.extend([field for field in OPTIONAL_LICENSE_FIELDS if field in data.columns])
core_cols.extend([
    'Address', 'City', 'State', 'Zip', 'Inspection Date', 'Inspection Type',
    'Results', 'Violations', 'Violation Category', 'Risk',
    'Latitude', 'Longitude', 'complaint_count', 'last_complaint', 'days_since_complaint'
])

data = data[[c for c in core_cols if c in data.columns]]
data = data.dropna(subset=['Inspection ID', 'Inspection Date'])

column_mapping = {
    'Inspection ID': 'inspection_id', 'DBA Name': 'name',
    'License #': 'license_number',
    'Facility Type': 'facility_type', 'LICENSE DESCRIPTION': 'license_description',
    'LICENSE STATUS': 'license_status', 'APPLICATION CREATED DATE': 'application_created_date',
    'DATE ISSUED': 'date_issued', 'LICENSE TERM START DATE': 'license_term_start_date',
    'LICENSE TERM EXPIRATION DATE': 'license_term_end_date', 'LICENSE APPROVED FOR ISSUANCE': 'license_approved_for_issuance',
    'PAYMENT DATE': 'payment_date', 'CONDITIONAL APPROVAL': 'conditional_approval',
    'APPLICATION TYPE': 'app_type', 'Address': 'address', 'City': 'city',
    'State': 'state', 'Zip': 'zip', 'Inspection Date': 'inspection_date',
    'Inspection Type': 'inspection_type', 'Results': 'results', 'Violations': 'violations',
    'Violation Category': 'violation_category', 'Risk': 'risk', 'Latitude': 'latitude',
    'Longitude': 'longitude'
}
data = data.rename(columns=column_mapping)
data.insert(0, 'id', range(1, len(data) + 1))

data.to_csv('clean_dataset.csv', index=False)

print(f"Cleaned dataset: {len(data):,} records")
print(f"Removed {duplicate_inspections:,} duplicate inspections")
print(f"Removed {duplicate_licenses:,} duplicate licenses")
print(f"Merged {(data['license_description'].notna().sum() if 'license_description' in data.columns else 0):,} with license data")
print(f"Added complaint data for {(data['complaint_count'] > 0).sum():,} locations")

with open('data_report.txt', 'w') as f:
    f.write(f"Data Quality Report - {pd.Timestamp.now()}\n\n\n")
    
    f.write(f"Final Dataset: {len(data):,} records\n")
    f.write(f"Date range: {data['inspection_date'].min()} to {data['inspection_date'].max()}\n\n")
    
    f.write("Results Distribution:\n")
    f.write(data['results'].value_counts().to_string() + "\n\n")
    
    f.write("Violation Categories:\n")
    f.write(data['violation_category'].value_counts().to_string() + "\n\n")
    
    f.write(f"Locations with complaints: {(data['complaint_count'] > 0).sum():,}\n")
    f.write(f"Average complaints per location: {data['complaint_count'].mean():.1f}\n")
    f.write(f"Max complaints at one location: {data['complaint_count'].max()}\n\n")
    
    missing = data.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        f.write("Missing Values:\n")
        f.write(missing.to_string())
    else:
        f.write("No missing values in core fields\n")
