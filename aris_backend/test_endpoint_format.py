from django.test import RequestFactory
from apps.results.api.views import UploadHistoryView
from apps.results.models import UploadLog
import json

print("=" * 60)
print("Testing /api/uploads/ Endpoint Response Format")
print("=" * 60)

# Check database
print(f"\n✓ Database check:")
total_uploads = UploadLog.objects.count()
print(f"  Total uploads in DB: {total_uploads}")

if total_uploads > 0:
    print(f"  Recent uploads:")
    for u in UploadLog.objects.order_by('-uploaded_at')[:3]:
        print(f"    - ID: {u.id}, Filename: {u.filename}, Status: {u.status}")

# Test the API endpoint
print(f"\n✓ Testing API endpoint response format:")
factory = RequestFactory()
request = factory.get('/api/uploads/')

view = UploadHistoryView.as_view()
response = view(request)

print(f"  Response status: {response.status_code}")

# Parse the response
response_data = response.data
print(f"  Response type: {type(response_data)}")

# Check the structure
if isinstance(response_data, dict):
    print(f"  ✅ Response is a dictionary (correct format)")
    print(f"  Keys: {list(response_data.keys())}")
    if 'data' in response_data:
        print(f"  ✅ Has 'data' key")
        print(f"    - data type: {type(response_data['data'])}")
        print(f"    - data length: {len(response_data['data'])}")
    else:
        print(f"  ❌ Missing 'data' key")
elif isinstance(response_data, list):
    print(f"  ⚠️  Response is a list (old format)")
    print(f"    - length: {len(response_data)}")
else:
    print(f"  ❌ Unexpected response type: {type(response_data)}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
