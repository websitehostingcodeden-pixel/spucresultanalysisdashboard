import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.services.snapshot import SnapshotManager
from apps.results.models import UploadLog, AnalyticsSnapshot

upload = UploadLog.objects.get(id=36)
print(f'Rebuilding snapshot for upload {upload.id}...')
SnapshotManager.compute_and_cache_upload_analytics(upload.id)
print('✓ Snapshot rebuilt successfully')

# Verify  
snapshot = AnalyticsSnapshot.objects.filter(upload_log=upload).first()
if snapshot:
    toppers = json.loads(snapshot.toppers_data) if isinstance(snapshot.toppers_data, str) else snapshot.toppers_data
    college_topper = toppers.get('college', [{}])[0]
    print(f"\nVerification - Top topper:")
    print(f"  Name: {college_topper.get('student_name')}")
    subjects = college_topper.get('subject_marks', {})
    print(f"  Subjects: {len(subjects)} - {list(subjects.keys())}")
    print(f"  Marks: {subjects}")
