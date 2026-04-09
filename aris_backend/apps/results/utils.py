import os
from django.conf import settings


def get_upload_path():
    """Get the upload directory path"""
    return settings.MEDIA_ROOT


def validate_file_size(file):
    """Validate file size against MAX_FILE_SIZE setting"""
    if file.size > settings.MAX_FILE_SIZE:
        return False, f"File size exceeds {settings.MAX_FILE_SIZE / 1024 / 1024}MB limit"
    return True, None


def validate_file_extension(file, allowed_extensions=None):
    """Validate file extension"""
    if allowed_extensions is None:
        allowed_extensions = [".xlsx", ".xls"]
    
    _, ext = os.path.splitext(file.name)
    if ext.lower() not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    return True, None
