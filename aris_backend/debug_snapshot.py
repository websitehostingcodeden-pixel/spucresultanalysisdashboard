import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import StudentResult, AnalyticsSnapshot
import json

# Check if any records have subject_marks_data populated
print("=== Checking StudentResult records ===")
records_with_marks = StudentResult.objects.exclude(subject_marks_data__isnull=True).exclude(subject_marks_data={})
print(f"Records with subject marks: {records_with_marks.count()}")

if records_with_marks.exists():
    r = records_with_marks.first()
    print(f"\nSample record with marks:")
    print(f"  Reg: {r.reg_no}")
    print(f"  Stream: {r.stream}")
    print(f"  Subject marks: {r.subject_marks_data}")

# Check science stream records
print("\n=== Science Stream Records ===")
science_records = StudentResult.objects.filter(stream='SCIENCE')
print(f"Science records: {science_records.count()}")
if science_records.exists():
    r = science_records.first()
    print(f"First science record:")
    print(f"  Reg: {r.reg_no}")
    print(f"  Subject marks: {r.subject_marks_data}")

# Check the latest snapshot
print("\n=== Checking AnalyticsSnapshot ===")
snapshots = AnalyticsSnapshot.objects.all().order_by('-created_at')
if snapshots.exists():
    snapshot = snapshots.first()
    print(f"Latest snapshot:")
    print(f"  ID: {snapshot.id}")
    print(f"  Scope: {snapshot.scope}")
    toppers = snapshot.analytics_data.get('toppers', {})
    
    for category in ['college', 'science', 'commerce']:
        toppers_list = toppers.get(category, [])
        if toppers_list:
            first = toppers_list[0]
            print(f"\n  {category.upper()} - First topper ({first.get('reg_no')}):")
            print(f"    Has stream: {'stream' in first}")
            print(f"    Has grand_total: {'grand_total' in first}")
            print(f"    Has subject_marks: {'subject_marks' in first}")
