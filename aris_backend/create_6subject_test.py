import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import StudentResult, UploadLog, AnalyticsSnapshot

# Clear existing data
StudentResult.objects.all().delete()
AnalyticsSnapshot.objects.all().delete()

# Create a synthetic upload
upload = UploadLog.objects.create(
    filename='test_6_subjects.xlsx',
    status='SUCCESS',
    records_processed=10,
    records_kept=10,
    retention_rate=100.0
)

# Create test records with 6 subjects
test_records = [
    {
        'reg_no': 'TEST001',
        'student_name': 'Test Student 1',
        'stream': 'SCIENCE',
        'section': 'A',
        'grand_total': 600.0,
        'percentage': 1.0,  # 100%
        'result_class': 'DISTINCTION',
        'subject_marks_data': {
            'ENGLISH': 100.0,
            'PHYSICS': 100.0,
            'CHEMISTRY': 100.0,
            'MATHEMATICS': 100.0,
            'BIOLOGY': 100.0,
            'SOCIAL_STUDIES': 100.0
        }
    },
    {
        'reg_no': 'TEST002',
        'student_name': 'Test Student 2',
        'stream': 'COMMERCE',
        'section': 'B',
        'grand_total': 570.0,
        'percentage': 0.95,
        'result_class': 'FIRST_CLASS',
        'subject_marks_data': {
            'ENGLISH': 95.0,
            'ECONOMICS': 95.0,
            'BUSINESS_STUDIES': 95.0,
            'MATHEMATICS': 95.0,
            'ACCOUNTING': 95.0,
            'HINDI': 95.0
        }
    },
]

for record_data in test_records:
    StudentResult.objects.create(
        upload_log=upload,
        **record_data
    )

print(f"Created {len(test_records)} test records with upload ID {upload.id}")
print("Records have 6 subjects each")

# Now recompute analytics snapshot
from apps.results.services.snapshot import SnapshotManager

result = SnapshotManager.compute_and_cache_upload_analytics(upload.id)
print(f"Snapshot recomputation: {result}")

if result['success']:
    # Verify toppers have all 6 subjects
    from apps.results.models import AnalyticsSnapshot
    snapshot = AnalyticsSnapshot.objects.get(id=result['snapshot_id'])
    toppers = snapshot.analytics_data.get('toppers', {})
    
    for category in ['college', 'science', 'commerce']:
        toppers_list = toppers.get(category, [])
        if toppers_list:
            first = toppers_list[0]
            subject_count = len(first.get('subject_marks', {}))
            print(f"  {category}: {first.get('student_name')} has {subject_count} subjects")
