import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.core.cache import cache
from apps.results.models import AnalyticsSnapshot, StudentResult, UploadLog

print('Clearing caches...')
cache.clear() 
print('✓ Caches cleared\n')

upload = UploadLog.objects.get(id=36)
snapshot = AnalyticsSnapshot.objects.filter(upload_log=upload).first()
if snapshot:
    print(f'Snapshot ID: {snapshot.id}')
    print(f'Snapshot model fields: {[f.name for f in snapshot._meta.get_fields()]}')
    
    # Get the topper data
    topper_list = snapshot.toppers if hasattr(snapshot, 'toppers') else None
    if topper_list:
        toppers = json.loads(topper_list) if isinstance(topper_list, str) else topper_list
        college_topper = toppers.get('college', [{}])[0]
        print(f'\nCollege topper:')
        print(f"  Name: {college_topper.get('student_name')}")
        subjects = college_topper.get('subject_marks', {})
        print(f"  Subjects: {len(subjects)} - {list(subjects.keys())}")
    else:
        print("No toppers attribute found")
        print(f"Snapshot dict: {snapshot.__dict__}")
