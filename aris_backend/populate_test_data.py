#!/usr/bin/env python
"""
Populate Database with Test Data for Analytics Testing

This script bypasses the upload process and directly creates clean test records
in the database for analytics testing.
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.results.models import StudentResult, UploadLog
from datetime import datetime, timedelta


def populate_test_data():
    """Create test records in database"""
    print("\n" + "="*70)
    print("📊 POPULATING TEST DATA INTO DATABASE")
    print("="*70)
    
    # Clear existing data (optional)
    StudentResult.objects.all().delete()
    UploadLog.objects.all().delete()
    
    # Create upload log
    upload_log = UploadLog.objects.create(
        filename="test_edge_cases.xlsx",
        status="SUCCESS",
        records_processed=8,
        records_kept=8,
        duplicates_removed=0,
        retention_rate=100.0,
        section_mismatches=5,
        total_mismatches=0,
        percentage_mismatches=1,
        alternate_identifiers_found=1
    )
    print(f"✓ Created upload log: {upload_log.filename}")
    
    # Test data - SCIENCE students
    science_students = [
        {
            "reg_no": "17SC001",
            "section": "A",
            "stream": "SCIENCE",
            "percentage": 95.2,
            "grand_total": 571,
            "result_class": "DISTINCTION",
        },
        {
            "reg_no": "17SC002",
            "section": "C",
            "stream": "SCIENCE",
            "percentage": 92.5,
            "grand_total": 555,
            "result_class": "DISTINCTION",
        },
        {
            "reg_no": "17SC003",
            "section": "B",
            "stream": "SCIENCE",
            "percentage": 88.3,
            "grand_total": 530,
            "result_class": "FIRST_CLASS",
        },
        {
            "reg_no": "17SC004",
            "section": "B",
            "stream": "SCIENCE",
            "percentage": 87.1,
            "grand_total": 523,
            "result_class": "FIRST_CLASS",
        },
        {
            "reg_no": "17SC005",
            "section": "A",
            "stream": "SCIENCE",
            "percentage": 91.6,
            "grand_total": 550,
            "result_class": "DISTINCTION",
        },
    ]
    
    # Test data - COMMERCE students
    commerce_students = [
        {
            "reg_no": "17CO001",
            "section": "X",
            "stream": "COMMERCE",
            "percentage": 97.2,
            "grand_total": 486,
            "result_class": "DISTINCTION",
        },
        {
            "reg_no": "17CO002",
            "section": "X",
            "stream": "COMMERCE",
            "percentage": 94.6,
            "grand_total": 473,
            "result_class": "DISTINCTION",
        },
        {
            "reg_no": "17CO003",
            "section": "Y",
            "stream": "COMMERCE",
            "percentage": 85.0,
            "grand_total": 425,
            "result_class": "FIRST_CLASS",
        },
    ]
    
    # Create student records
    records_created = 0
    
    for i, data in enumerate(science_students + commerce_students, 1):
        try:
            student = StudentResult.objects.create(
                reg_no=data['reg_no'],
                section=data.get('section', 'N/A'),
                stream=data.get('stream', 'SCIENCE'),
                percentage=data['percentage'],
                grand_total=data['grand_total'],
                result_class=data['result_class'],
                data_completeness_score=25,  # All essential fields filled
                was_duplicate=False,
                percentage_was_filled=True,
            )
            
            records_created += 1
            status_icon = "✓" if data['result_class'] == 'DISTINCTION' else "•"
            print(f"{status_icon} {data['reg_no']}: {data['percentage']}% - {data['result_class']}")
            
        except Exception as e:
            print(f"❌ Error creating {data['reg_no']}: {str(e)}")
    
    print(f"\n✅ Created {records_created} test records")
    print(f"\n📊 Data Summary:")
    print(f"   • Total records: {StudentResult.objects.count()}")
    print(f"   • SCIENCE: {StudentResult.objects.filter(stream='SCIENCE').count()}")
    print(f"   • COMMERCE: {StudentResult.objects.filter(stream='COMMERCE').count()}")
    print(f"   • Sections: {', '.join(sorted(set(StudentResult.objects.values_list('section', flat=True))))}")
    
    print("\n" + "="*70)
    print("✅ TEST DATA POPULATED SUCCESSFULLY")
    print("="*70)
    print("\n📚 Now run the analytics test:")
    print("   python test_analytics.py")


if __name__ == "__main__":
    populate_test_data()
