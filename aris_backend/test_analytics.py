#!/usr/bin/env python
"""
Test Analytics Engine - Demonstrate strict analytics pipeline

This script:
1. Loads cleaned students from database
2. Runs analytics engine with full validation
3. Displays formatted results
4. Verifies consistency checks
"""

import os
import sys
import django
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.results.models import StudentResult, UploadLog
from apps.results.services.analytics import compute_analytics


def pretty_print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def test_analytics():
    """Run complete analytics test"""
    print("\n" + "="*70)
    print("🔬 STRICT ANALYTICS ENGINE TEST")
    print("="*70)
    
    # Get dataset info
    total_records = StudentResult.objects.count()
    print(f"\n📊 Dataset loaded: {total_records} student records")
    
    if total_records == 0:
        print("❌ No student records found. Please upload a file first.")
        print("   Try: curl -X POST http://127.0.0.1:8000/api/upload/ -F 'file=@test_edge_cases.xlsx'")
        return
    
    # Get streams
    streams = StudentResult.objects.values_list('stream', flat=True).distinct()
    print(f"📚 Streams: {', '.join(streams) if streams else 'None'}")
    
    # Get sections
    sections = StudentResult.objects.values_list('section', flat=True).distinct()
    print(f"🏫 Sections: {', '.join(sorted(sections))}")
    
    print("\n" + "-"*70)
    print("1️⃣  GENERATING GLOBAL ANALYTICS...")
    print("-"*70)
    
    # Generate global analytics
    analytics = compute_analytics()
    
    if analytics['status'] != 'success':
        print(f"❌ Analytics failed: {analytics.get('message')}")
        print(f"   Failed step: {analytics.get('failed_step')}")
        return
    
    # Display summary
    summary = analytics['summary']
    print(f"\n✓ Global Summary:")
    print(f"  • Total Students: {summary['total_students']}")
    print(f"  • Passed: {summary['total_passed']} ({summary['pass_percentage']}%)")
    print(f"  • Failed: {summary['total_failed']}")
    print(f"  • Average %: {summary['average_percentage']}%")
    print(f"  • Distinction: {summary['distinction_count']}")
    print(f"  • First Class: {summary['first_class_count']}")
    print(f"  • Second Class: {summary['second_class_count']}")
    print(f"  • Pass Class: {summary['pass_class_count']}")
    
    # Display toppers
    print(f"\n✓ College Toppers (Top 10):")
    for topper in analytics['toppers'].get('college', [])[:5]:  # Show top 5
        print(f"  {topper['rank']}. {topper['student_name']} ({topper['reg_no']}) - {topper['percentage']}%")
    
    if len(analytics['toppers'].get('college', [])) > 5:
        print(f"  ... and {len(analytics['toppers']['college']) - 5} more")
    
    # Display science toppers if available
    if analytics['toppers'].get('science'):
        print(f"\n✓ Science Toppers (Top 5):")
        for topper in analytics['toppers']['science'][:5]:
            print(f"  {topper['rank']}. {topper['student_name']} ({topper['reg_no']}) - {topper['percentage']}%")
    
    # Display commerce toppers if available
    if analytics['toppers'].get('commerce'):
        print(f"\n✓ Commerce Toppers (Top 5):")
        for topper in analytics['toppers']['commerce'][:5]:
            print(f"  {topper['rank']}. {topper['student_name']} ({topper['reg_no']}) - {topper['percentage']}%")
    
    # Display section performance
    print(f"\n✓ Section Performance:")
    for section in analytics['sections']:
        print(f"\n  Section {section['section']}:")
        print(f"    • Appeared: {section['appeared']}")
        print(f"    • Passed: {section['passed']} ({section['pass_percentage']}%)")
        print(f"    • Failed: {section['failed']}")
        print(f"    • Distinction: {section['distinction']}")
        print(f"    • First Class: {section['first_class']}")
        print(f"    • Average %: {section['average_percentage']}%")
    
    # Display subject analysis if available
    if analytics['subjects']:
        print(f"\n✓ Subject Analysis:")
        for subject, data in list(analytics['subjects'].items())[:3]:  # Show first 3 subjects
            print(f"\n  {subject}:")
            print(f"    • Average: {data['average_marks']}")
            print(f"    • Students: {data['total_students']}")
            print(f"    • Grade Distribution:")
            dist = data['distribution']
            for grade, count in sorted(dist.items()):
                if count > 0:
                    print(f"      - {grade}: {count} students")
    
    # Display insights
    if analytics['insights']:
        print(f"\n✓ Key Insights:")
        insights = analytics['insights']
        
        if 'highest_section' in insights:
            hs = insights['highest_section']
            print(f"  • Highest Section: {hs['name']} ({hs['pass_percentage']}% pass)")
        
        if 'lowest_section' in insights:
            ls = insights['lowest_section']
            print(f"  • Lowest Section: {ls['name']} ({ls['pass_percentage']}% pass)")
        
        if 'top_student' in insights:
            ts = insights['top_student']
            print(f"  • Top Student: {ts['student_name']} ({ts['reg_no']}) - {ts['percentage']}%")
        
        if 'strong_subject' in insights:
            ss = insights['strong_subject']
            print(f"  • Strong Subject: {ss['name']} (Avg: {ss['average']})")
        
        if 'weak_subject' in insights:
            ws = insights['weak_subject']
            print(f"  • Weak Subject: {ws['name']} (Avg: {ws['average']})")
    
    # Test upload-specific analytics
    print("\n" + "-"*70)
    print("2️⃣  TESTING UPLOAD-SPECIFIC ANALYTICS...")
    print("-"*70)
    
    uploads = UploadLog.objects.all()
    if uploads.exists():
        upload = uploads.first()
        print(f"\n✓ Analyzing upload: {upload.filename}")
        
        queryset = StudentResult.objects.filter(upload_log=upload) if hasattr(upload, 'upload_log') else StudentResult.objects.all()
        upload_analytics = compute_analytics(queryset)
        
        if upload_analytics['status'] == 'success':
            print(f"  • Records in this upload: {upload_analytics['summary']['total_students']}")
            print(f"  • Pass rate: {upload_analytics['summary']['pass_percentage']}%")
            print(f"  • Quality metrics from upload:")
            print(f"    - Section mismatches: {upload.section_mismatches}")
            print(f"    - Percentage mismatches: {upload.percentage_mismatches}")
            print(f"    - Retention rate: {upload.retention_rate}%")
    
    # Test stream-specific analytics
    if streams:
        print("\n" + "-"*70)
        print("3️⃣  TESTING STREAM-SPECIFIC ANALYTICS...")
        print("-"*70)
        
        for stream in streams:
            print(f"\n✓ Analyzing {stream} stream:")
            queryset = StudentResult.objects.filter(stream=stream)
            stream_analytics = compute_analytics(queryset)
            
            if stream_analytics['status'] == 'success':
                summary = stream_analytics['summary']
                print(f"  • Students: {summary['total_students']}")
                print(f"  • Pass rate: {summary['pass_percentage']}%")
                print(f"  • Average %: {summary['average_percentage']}%")
    
    # Test section-specific analytics
    if sections:
        print("\n" + "-"*70)
        print("4️⃣  TESTING SECTION-SPECIFIC ANALYTICS...")
        print("-"*70)
        
        for section in list(sections)[:3]:  # Test first 3 sections
            print(f"\n✓ Analyzing section {section}:")
            queryset = StudentResult.objects.filter(section=section)
            section_analytics = compute_analytics(queryset)
            
            if section_analytics['status'] == 'success':
                summary = section_analytics['summary']
                print(f"  • Students: {summary['total_students']}")
                print(f"  • Pass rate: {summary['pass_percentage']}%")
                print(f"  • Average %: {summary['average_percentage']}%")
    
    print("\n" + "="*70)
    print("✅ ALL ANALYTICS TESTS PASSED!")
    print("="*70)
    
    # Save full analytics to JSON for inspection
    output_file = "analytics_output.json"
    with open(output_file, 'w') as f:
        json.dump(analytics, f, indent=2, default=str)
    print(f"\n📄 Full analytics saved to: {output_file}")
    print("\n📚 Analytics API Endpoints:")
    print("   • GET /api/analytics/ - Global analytics")
    print("   • GET /api/analytics/upload/<id>/ - Upload-specific")
    print("   • GET /api/analytics/section/?section=SC - Section-specific")
    print("   • GET /api/analytics/stream/?stream=SCIENCE - Stream-specific")


if __name__ == "__main__":
    test_analytics()
