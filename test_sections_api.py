#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, 'd:\\spuc-RA ARIS\\aris_backend')
django.setup()

from apps.results.models import UploadLog
from apps.results.api.views import SectionsView
from django.test import RequestFactory
import json

factory = RequestFactory()

# Get the first upload
uploads = UploadLog.objects.all()[:1]

if uploads:
    upload = uploads[0]
    request = factory.get(f'/api/sections/{upload.id}/')
    
    view = SectionsView.as_view()
    response = view(request, upload_id=upload.id)
    
    print(f"✅ Upload ID: {upload.id}")
    print(f"✅ Status Code: {response.status_code}")
    
    if hasattr(response, 'data') and isinstance(response.data, dict):
        print(f"✅ Response Keys: {list(response.data.keys())}")
        
        if 'sections' in response.data:
            sections = response.data['sections']
            print(f"✅ Number of sections: {len(sections)}")
            
            if sections:
                first_section = sections[0]
                print(f"\n✅ Sample Section Structure:")
                print(json.dumps(first_section, indent=2)[:500])
else:
    print("❌ No uploads found in database")
