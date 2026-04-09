from django.db import models
import json


class StudentResult(models.Model):
    """Model for storing student results from Excel uploads"""

    STREAM_CHOICES = [
        ("SCIENCE", "Science"),
        ("COMMERCE", "Commerce"),
    ]
    
    RESULT_CLASS_CHOICES = [
        ("DISTINCTION", "Distinction"),
        ("FIRST_CLASS", "First Class"),
        ("SECOND_CLASS", "Second Class"),
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
        ("INCOMPLETE", "Incomplete"),
    ]

    reg_no = models.CharField(max_length=50, unique=True, db_index=True)
    student_name = models.CharField(max_length=255, blank=True, null=True)
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES)
    section = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    
    # Link to upload (tracks which upload this record came from)
    upload_log = models.ForeignKey(
        'UploadLog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )
    
    # Core scores
    percentage = models.FloatField(blank=True, null=True)
    grand_total = models.FloatField(blank=True, null=True, db_index=True)
    
    # Auto-derived classification
    result_class = models.CharField(
        max_length=20,
        choices=RESULT_CLASS_CHOICES,
        default="INCOMPLETE",
        db_index=True
    )
    
    # Subject marks (JSON field to store all subject scores)
    subject_marks_data = models.JSONField(default=dict, blank=True)
    
    # Language choice (K/H/S - Kannada/Hindi/Sanskrit)
    language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('K', 'Kannada'),
            ('H', 'Hindi'),
            ('S', 'Sanskrit'),
        ]
    )
    
    # Data quality tracking
    data_completeness_score = models.IntegerField(default=0)
    was_duplicate = models.BooleanField(default=False)
    percentage_was_filled = models.BooleanField(default=False)
    
    # Versioning (PRODUCTION: track what processed this record)
    data_version = models.CharField(max_length=20, default="v1.0")
    processing_version = models.CharField(max_length=50, default="cleaner_v1")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-grand_total"]
        indexes = [
            models.Index(fields=["reg_no"]),
            models.Index(fields=["stream"]),
            models.Index(fields=["-grand_total"]),
            models.Index(fields=["result_class"]),
        ]

    def __str__(self):
        return f"{self.reg_no} - {self.stream} - {self.result_class}"


class UploadLog(models.Model):
    """Track file uploads and processing with quality metrics"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("SUCCESS_WITH_WARNINGS", "Success With Warnings"),
        ("FAILED", "Failed"),
    ]

    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PENDING")
    
    # Processing stats
    records_processed = models.IntegerField(default=0)
    records_kept = models.IntegerField(default=0)
    
    # Quality metrics - Data Integrity
    invalid_reg_no_removed = models.IntegerField(default=0)
    duplicates_removed = models.IntegerField(default=0)
    missing_grand_total_removed = models.IntegerField(default=0)
    missing_percentage_filled = models.IntegerField(default=0)
    invalid_percentage_corrected = models.IntegerField(default=0)
    
    # Quality metrics - Data Validation (NEW)
    section_mismatches = models.IntegerField(default=0)
    total_mismatches = models.IntegerField(default=0)
    percentage_mismatches = models.IntegerField(default=0)
    alternate_identifiers_found = models.IntegerField(default=0)
    
    # Quality score
    retention_rate = models.FloatField(default=0)  # Percentage of records kept
    
    # Versioning (PRODUCTION: track what version processed this)
    data_version = models.CharField(max_length=20, default="v1.0")
    processing_version = models.CharField(max_length=50, default="cleaner_v1")
    
    error_message = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["-uploaded_at"]),
        ]

    def __str__(self):
        return f"{self.filename} - {self.status} ({self.records_kept}/{self.records_processed})"


class AnalyticsSnapshot(models.Model):
    """
    PRODUCTION: Cache analytics results for fast retrieval.
    
    Instead of recomputing analytics every time:
    1. Compute once after upload
    2. Store snapshot
    3. API returns cached snapshot
    
    Benefits:
    - Fast API response (<100ms)
    - Consistent results
    - Traceable version of analytics
    - Can regenerate if needed
    """

    # Link to upload (NULL = global analytics)
    upload_log = models.OneToOneField(
        UploadLog,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True
    )

    # Scope of snapshot
    SCOPE_CHOICES = [
        ("GLOBAL", "Global (all students)"),
        ("STREAM", "By Stream (SCIENCE/COMMERCE)"),
        ("SECTION", "By Section"),
        ("UPLOAD", "Specific Upload"),
    ]
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="GLOBAL")
    scope_value = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    
    # Analytics data (JSON)
    analytics_data = models.JSONField()
    
    # Versioning
    analytics_version = models.CharField(max_length=50, default="analytics_v1")
    
    # Status
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list)
    
    # Timing
    computed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Traceability
    record_count = models.IntegerField(default=0)
    computation_time_ms = models.IntegerField(default=0)

    class Meta:
        ordering = ["-computed_at"]
        indexes = [
            models.Index(fields=["upload_log"]),
            models.Index(fields=["scope", "scope_value"]),
            models.Index(fields=["-computed_at"]),
        ]
        unique_together = [
            ["upload_log", "scope", "scope_value"],
        ]

    def __str__(self):
        if self.upload_log:
            return f"Snapshot: {self.upload_log.filename} ({self.scope})"
        return f"Snapshot: {self.scope} ({self.scope_value or 'global'})"

    def is_expired(self) -> bool:
        """Check if snapshot has expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
