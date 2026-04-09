#!/usr/bin/env python
"""Verify data exists for dashboard rendering"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, 'd:\\spuc-RA ARIS\\aris_backend')
django.setup()

from apps.results.models import StudentResult, UploadLog

# Check data
total_records = StudentResult.objects.count()
total_uploads = UploadLog.objects.count()

print("="*60)
print("DASHBOARD DATA AVAILABILITY CHECK")
print("="*60)
print(f"\n✅ Total StudentResult records: {total_records}")
print(f"✅ Total uploads: {total_uploads}")

if total_uploads > 0 and total_records > 0:
    print(f"\n✅ DATA EXISTS FOR DASHBOARD")
    print(f"   - {total_records} student records")
    print(f"   - {total_uploads} uploads available")
    print(f"\n✅ DASHBOARD WILL RENDER WITH DATA")
else:
    print(f"\n⚠️ No data found")

print("="*60)
