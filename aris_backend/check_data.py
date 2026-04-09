import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import StudentResult, UploadLog

print(f"Total uploads: {UploadLog.objects.count()}")
print(f"Total records: {StudentResult.objects.count()}")

if StudentResult.objects.exists():
    r = StudentResult.objects.first()
    print(f"\nFirst record:")
    print(f"  Name: {r.student_name}")
    print(f"  Stream: {r.stream}")
    print(f"  Grand Total: {r.grand_total}")
    print(f"  Subject Marks: {r.subject_marks_data}")
    print(f"  Percentage: {r.percentage}")
    
if UploadLog.objects.exists():
    u = UploadLog.objects.first()
    print(f"\nFirst upload:")
    print(f"  ID: {u.id}")
    print(f"  Total records: {u.total_records}")
    print(f"  Status: {u.status}")
