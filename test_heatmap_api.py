#!/usr/bin/env python
"""
Test the heatmap API to verify it returns grade distribution data
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_heatmap_api():
    """Test the heatmap endpoint"""
    print("🧪 Testing Heatmap API...")
    print("=" * 60)
    
    # Test 1: Get heatmap for PCMB A
    print("\n📊 TEST 1: Get heatmap for PCMB A (Grade Distribution Format)")
    try:
        response = requests.get(f"{BASE_URL}/heatmap/?section=PCMB%20A&format=grade-distribution")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            print(f"✓ Section: {data.get('data', {}).get('section')}")
            print(f"✓ Total Subjects: {data.get('data', {}).get('total_subjects')}")
            
            subjects = data.get('data', {}).get('subjects', [])
            if subjects:
                print(f"\n✓ Subject Data Format (first subject):")
                print(json.dumps(subjects[0], indent=2))
                print(f"\n✓ All Subjects in PCMB A:")
                for subject in subjects:
                    print(f"  - {subject['subject']}: "
                          f"DIST={subject['distinction']}, "
                          f"1ST={subject['i class']}, "
                          f"2ND={subject['ii class']}, "
                          f"3RD={subject['iii class']}, "
                          f"FAIL={subject['fail']}")
            else:
                print("⚠ No subjects found")
        else:
            print(f"✗ API Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    # Test 2: Get heatmap for PCMB B
    print("\n" + "=" * 60)
    print("\n📊 TEST 2: Get heatmap for PCMB B")
    try:
        response = requests.get(f"{BASE_URL}/heatmap/?section=PCMB%20B&format=grade-distribution")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            subjects = data.get('data', {}).get('subjects', [])
            print(f"✓ Subjects in PCMB B: {len(subjects)}")
            for subject in subjects:
                print(f"  - {subject['subject']}")
        else:
            print(f"✗ API Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    # Test 3: Test old flat format (compatibility)
    print("\n" + "=" * 60)
    print("\n📊 TEST 3: Get heatmap in flat format (legacy)")
    try:
        response = requests.get(f"{BASE_URL}/heatmap/?section=PCMB%20A&format=flat")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            records = data.get('data', [])
            print(f"✓ Total Records: {len(records)}")
            if records:
                print(f"✓ Record Format (first record):")
                print(json.dumps(records[0], indent=2))
        else:
            print(f"✗ API Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

if __name__ == "__main__":
    test_heatmap_api()
