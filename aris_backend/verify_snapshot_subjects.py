import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import AnalyticsSnapshot, UploadLog

upload = UploadLog.objects.get(id=36)
print(f"Upload: {upload.id} - {upload.filename}")

snapshot = AnalyticsSnapshot.objects.filter(upload_log=upload, scope='UPLOAD').first()
print(f"Snapshot found: {snapshot is not None}")

if snapshot:
    print(f"Analytics data length: {len(snapshot.analytics_data)}")
    try:
        data = json.loads(snapshot.analytics_data) if isinstance(snapshot.analytics_data, str) else snapshot.analytics_data
        print(f'Data keys: {list(data.keys())}')
        
        if 'toppers' in data:
            toppers = data['toppers']
            print(f'Toppers keys: {list(toppers.keys())}')
            if 'college' in toppers and toppers['college']:
                top = toppers['college'][0]
                print(f"Top topper: {top.get('student_name')}")
                subject_marks = top.get('subject_marks', {})
                print(f"Num subjects: {len(subject_marks)}")
                print(f"Subjects: {list(subject_marks.keys())}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Snapshot is None")
    snapshots = AnalyticsSnapshot.objects.filter(upload_log=upload)
    print(f"Total snapshots: {snapshots.count()}")
    for s in snapshots:
        print(f"  - Scope: {s.scope}, Value: {s.scope_value}")
