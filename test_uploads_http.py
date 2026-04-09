#!/usr/bin/env python
"""Quick test of the uploads endpoint"""
import requests
import json
import time

print("=" * 60)
print("Testing /api/uploads/ Endpoint (HTTP)")
print("=" * 60)

# Give server time to start if needed
time.sleep(1)

try:
    response = requests.get('http://localhost:8000/api/uploads/', timeout=5)
    
    print(f"\n✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Response is valid JSON")
        print(f"  Type: {type(data).__name__}")
        
        if isinstance(data, dict):
            print(f"✅ Response is a dictionary")
            print(f"   Keys: {list(data.keys())}")
            
            # Check for data key
            if 'data' in data:
                print(f"✅ Has 'data' key")
                uploads_list = data['data']
                print(f"   Uploads in data: {len(uploads_list)}")
                if len(uploads_list) > 0:
                    print(f"   First upload: {uploads_list[0]}")
            else:
                print(f"❌ No 'data' key found")
                print(f"   Full response: {data}")
        elif isinstance(data, list):
            print(f"⚠️  Response is a list (backward compat issue)")
            print(f"   Length: {len(data)}")
        else:
            print(f"❌ Unexpected type: {type(data)}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server at http://localhost:8000")
    print("   Make sure the backend server is running!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
