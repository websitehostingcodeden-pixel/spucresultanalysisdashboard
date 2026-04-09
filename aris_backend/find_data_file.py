import os, django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import UploadLog
from django.conf import settings

# List all Excel files  in the project
print("=== SEARCHING FOR DATA FILES ===")
for root, dirs, files in os.walk("d:\\spuc-RA ARIS"):
    # Skip virtual environments and caches
    if 'venv' in root or '__pycache__' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.xlsx') and 'PROCSSED' in file:
            full_path = os.path.join(root, file)
            print(f"\nFound: {full_path}")
            try:
                df = pd.read_excel(full_path, sheet_name=0, nrows=1)
                print(f"Columns: {list(df.columns)}")
            except Exception as e:
                print(f"Error reading: {e}")
