from apps.results.models import AnalyticsSnapshot
from apps.results.services.snapshot import SnapshotManager

# Delete all snapshots to force recomputation
deleted_count, _ = AnalyticsSnapshot.objects.all().delete()
print(f'Deleted {deleted_count} snapshots')

# Manually recompute analytics snapshot for upload_id=30
result = SnapshotManager.compute_and_cache_upload_analytics(30)
print(f'Recomputation: {result}')
