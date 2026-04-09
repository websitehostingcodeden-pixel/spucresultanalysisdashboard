from apps.results.models import UploadLog

for upload in UploadLog.objects.all().order_by('-id'):
    print(f"Upload {upload.id}: {upload.filename} - {upload.status}")
    print(f"  Records: {upload.records_processed} processed, kept={upload.records_kept}")
    if upload.error_message:
        print(f"  Error: {upload.error_message}")
