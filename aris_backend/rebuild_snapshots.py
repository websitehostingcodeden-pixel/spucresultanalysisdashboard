import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import AnalyticsSnapshot

# Delete all snapshots to force recomputation
deleted_count, _ = AnalyticsSnapshot.objects.all().delete()
print(f"Deleted {deleted_count} snapshots")

# Manually recompute analytics snapshot for upload_id=30
from apps.results.services.snapshot import SnapshotManager
result = SnapshotManager.compute_and_cache_upload_analytics(30)
print(f"Recomputation result: {result}")

if result['success']:
    print(f"New snapshot created/updated:")
    print(f"  - ID: {result['snapshot_id']}")
    print(f"  - Computation time: {result['computation_time_ms']}ms")
    print(f"  - Record count: {result['record_count']}")
