import os, django, json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.models import AnalyticsSnapshot, StudentResult

# Check the raw student data
print("=== RAW STUDENT DATA ===")
students = StudentResult.objects.all()[:3]
for student in students:
    print(f"\nStudent: {student.student_name}")
    if student.subject_marks_data:
        subjects = list(student.subject_marks_data.keys())
        print(f"  Subjects in data: {len(subjects)} - {subjects}")

# Check the topper analytics data
print("\n=== TOPPER ANALYTICS DATA ===")
snapshot = AnalyticsSnapshot.objects.first()
if snapshot and snapshot.toppers_data:
    toppers = json.loads(snapshot.toppers_data) if isinstance(snapshot.toppers_data, str) else snapshot.toppers_data
    for category in ['college', 'science', 'commerce']:
        if category in toppers and toppers[category]:
            print(f"\n{category.upper()} Toppers:")
            for idx, topper in enumerate(toppers[category][:2]):
                print(f"  #{idx+1}: {topper.get('student_name')} - {len(topper.get('subject_marks', {}))} subjects")
                subjects = list(topper.get('subject_marks', {}).keys())
                print(f"       Subjects: {subjects}")
