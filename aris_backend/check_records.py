from apps.results.models import StudentResult, UploadLog

upload = UploadLog.objects.get(id=30)
print(f"Upload 30 status: {upload.status}")
print(f"Records processed: {upload.records_processed}")

# Check records for this upload
records = StudentResult.objects.filter(upload_log=upload)
print(f"Records in DB for upload 30: {records.count()}")

# Check all records
all_records = StudentResult.objects.all()
print(f"Total StudentResult records: {all_records.count()}")

if all_records.exists():
    first = all_records.first()
    print(f"\nFirst record: {first.reg_no}")
    print(f"  Stream: {first.stream}")
    print(f"  Upload: {first.upload_log_id}")
    print(f"  Subject marks: {first.subject_marks_data}")
