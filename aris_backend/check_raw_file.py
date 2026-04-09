import os, django
import pandas as pd
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import UploadLog

# Read the actual real data file
upload = UploadLog.objects.get(id=36)
print(f"Upload: {upload.filename}")

# Try to find and read the file
base_path = "d:\\spuc-RA ARIS\\aris_backend"
file_path = os.path.join(base_path, "test_6_subjects_real.xlsx")

# If that doesn't exist, try to find the actual upload file
if not os.path.exists(file_path):
    # Check if there's a "PROCSSED DATA.xlsx" file anywhere
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if "PROCSSED" in file or "PROCESSED" in file:
                file_path = os.path.join(root, file)
                break

print(f"\nReading: {file_path}")
if os.path.exists(file_path):
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData shape: {df.shape}")
    print(f"\nColumn types:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")
    
    # Check first few rows
    print(f"\nFirst row:")
    print(df.iloc[0])
else:
    print("File not found")
