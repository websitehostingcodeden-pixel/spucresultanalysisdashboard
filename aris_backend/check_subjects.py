from apps.results.models import StudentResult

# Get first record with subject marks
r = StudentResult.objects.exclude(subject_marks_data__isnull=True).exclude(subject_marks_data={}).first()
if r:
    print(f"Record: {r.reg_no}")
    print(f"Subject marks stored: {len(r.subject_marks_data)} subjects")
    for subject, marks in r.subject_marks_data.items():
        print(f"  - {subject}: {marks}")
else:
    print("No records with subject marks found")
