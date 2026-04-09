import os, django
import pandas as pd
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import UploadLog, StudentResult

# Check existing uploads
print("=== EXISTING UPLOADS ===")
uploads = UploadLog.objects.all().order_by('-uploaded_at')[:5]
for upload in uploads:
    student_count = StudentResult.objects.filter(upload_log=upload).count()
    print(f"Upload ID {upload.id}: {upload.filename} - {student_count} students - Status: {upload.status}")
    
    # Check subject counts for this upload
    students = StudentResult.objects.filter(upload_log=upload)[:2]
    for student in students:
        if student.subject_marks_data:
            subjects = list(student.subject_marks_data.keys())
            print(f"  - {student.student_name}: {len(subjects)} subjects - {subjects}")

# Find the most recent upload that's used for toppers
print("\n=== MOST RECENT UPLOAD DETAILS ===")
latest_upload = UploadLog.objects.order_by('-uploaded_at').first()
if latest_upload:
    print(f"Latest upload ID: {latest_upload.id}")
    print(f"File: {latest_upload.filename}")
    students = StudentResult.objects.filter(upload_log=latest_upload).order_by('-grand_total')[:3]
    print(f"\nTop 3 students:")
    for student in students:
        if student.subject_marks_data:
            print(f"  {student.student_name}: {len(student.subject_marks_data)} subjects")
