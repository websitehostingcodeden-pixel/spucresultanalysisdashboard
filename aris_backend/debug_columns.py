import os, django
import pandas as pd
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import UploadLog

# Read the actual uploaded file
upload = UploadLog.objects.filter(file_path__isnull=False).first()
if upload:
    file_path = os.path.join(settings.MEDIA_ROOT, upload.file_path.name) if hasattr(upload.file_path, 'name') else str(upload.file_path)
    print(f"Reading file: {file_path}")
    
    # Try reading with different approaches
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"\nColumns in file: {list(df.columns)}")
        print(f"Column data types:\n{df.dtypes}")
        
        # Check the analyzer's logic
        subject_keywords = {'marks_', 'english', 'maths', 'science', 'history', 'geography', 'civics', 
                           'physics', 'chemistry', 'biology', 'hindi', 'sanskrit', 'social', 'studies',
                           'economics', 'environmental', 'language', 'literature', 'computer', 'IT',
                           'accountancy', 'business', 'statistics', 'psychology'}
        
        numeric_cols = [
            col for col in df.columns 
            if any(keyword in col.lower() for keyword in subject_keywords)
            and pd.api.types.is_numeric_dtype(df[col])
        ]
        
        print(f"\nNumeric subject columns detected: {numeric_cols}")
        print(f"Number of subjects: {len(numeric_cols)}")
        
    except Exception as e:
        print(f"Error: {e}")
