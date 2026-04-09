"""
Test the complete upload pipeline with real 6-subject Excel file
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import UploadLog, StudentResult
from apps.results.services.analyzer import process_upload
from django.core.files.uploadedfile import SimpleUploadedFile

# Read the Excel file
excel_path = 'test_6_subjects_real.xlsx'
if not os.path.exists(excel_path):
    print(f"ERROR: {excel_path} not found")
    exit(1)

# Create upload log
upload = UploadLog.objects.create(
    filename='test_6_subjects_real.xlsx',
    status='PENDING'
)

print(f"Created upload log: ID={upload.id}")

# Open and process the file
with open(excel_path, 'rb') as f:
    file_content = f.read()

# Create SimpleUploadedFile
uploaded_file = SimpleUploadedFile(
    name='test_6_subjects_real.xlsx',
    content=file_content,
    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Process upload
success, records_created, quality_metrics, error_msg = process_upload(uploaded_file, upload)

if success:
    print(f"Upload processed successfully")
    print(f"  Records created: {records_created}")
    print(f"  Records kept: {len(StudentResult.objects.filter(upload_log=upload))}")
    
    # Check actual records
    records = StudentResult.objects.filter(upload_log=upload)
    for record in records:
        subject_count = len(record.subject_marks_data)
        print(f"\n  Record: {record.reg_no}")
        print(f"    Subjects extracted: {subject_count}")
        for subject, marks in list(record.subject_marks_data.items())[:6]:
            print(f"      - {subject}: {marks}")
else:
    print(f"Upload failed: {error_msg}")
