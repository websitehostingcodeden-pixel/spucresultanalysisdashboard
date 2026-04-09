"""
Verify 6 subjects are properly extracted and available in API response
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/toppers/32/"

try:
    response = requests.get(API_URL, timeout=10)
    data = response.json()
    
    print("=" * 60)
    print("6-SUBJECT EXTRACTION VERIFICATION")
    print("=" * 60)
    print()
    
    if data.get("status") == "success":
        toppers = data.get("toppers", {})
        
        # Check college toppers
        college = toppers.get("college", [])
        if college:
            topper = college[0]
            subjects = topper.get("subject_marks", {})
            subject_count = len(subjects)
            subject_names = list(subjects.keys())
            
            print(f"COLLEGE TOPPER: {topper.get('student_name')}")
            print(f"Stream: {topper.get('stream')}")
            print(f"Grand Total: {topper.get('grand_total')}")
            print(f"Percentage: {topper.get('percentage') * 100:.2f}%")
            print(f"\nSubjects ({subject_count} total, displaying first 6):")
            
            for i, (subject, marks) in enumerate(list(subjects.items())[:6], 1):
                display_name = subject.replace('_', ' ')
                print(f"  {i}. {display_name}: {marks}")
            
            if subject_count == 6:
                print("\n✓ SUCCESS: Exactly 6 subjects extracted")
            elif subject_count > 6:
                print(f"\n✓ SUCCESS: {subject_count} subjects extracted (will display first 6)")
            else:
                print(f"\n✗ FAILED: Only {subject_count} subjects extracted (need 6)")
        else:
            print("✗ FAILED: No college toppers found")
    else:
        print(f"✗ API Error: {data.get('message')}")
        
except Exception as e:
    print(f"✗ ERROR: {str(e)}")

print()
print("=" * 60)
