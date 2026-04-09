from apps.results.models import AnalyticsSnapshot
from apps.results.services.snapshot import SnapshotManager
import os

# Suppress encoding issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Delete all snapshots
deleted, _ = AnalyticsSnapshot.objects.all().delete()

# Rebuild
result = SnapshotManager.compute_and_cache_upload_analytics(30)
print(f"Success: {result['success']}")
if result['success']:
    print(f"Snapshot ID: {result['snapshot_id']}")
