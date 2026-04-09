#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, 'aris_backend')
django.setup()

from apps.results.models import UploadLog

print(f'Total uploads: {UploadLog.objects.count()}')
print('Recent uploads:')
for u in UploadLog.objects.order_by('-uploaded_at')[:5]:
    print(f'  - ID: {u.id}, Filename: {u.filename}, Status: {u.status}')
