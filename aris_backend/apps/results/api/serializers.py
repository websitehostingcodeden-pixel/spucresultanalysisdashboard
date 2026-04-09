"""
STRICT API SERIALIZERS

All responses include strict versioning and traceability fields.
Designed for frontend consumption with exact formatting.
"""

from rest_framework import serializers
from apps.results.models import StudentResult, UploadLog, AnalyticsSnapshot


# ===== STRICT RESPONSE WRAPPERS =====

class VersionInfoSerializer(serializers.Serializer):
    """Versioning information included in ALL responses"""
    data_version = serializers.CharField()
    processing_version = serializers.CharField()
    analytics_version = serializers.CharField(required=False)
    api_version = serializers.CharField(default="1.0")


class CacheInfoSerializer(serializers.Serializer):
    """Cache metadata for API responses"""
    was_cached = serializers.BooleanField()
    cached_at = serializers.DateTimeField(required=False)
    expires_at = serializers.DateTimeField(required=False)
    response_time_ms = serializers.IntegerField()
    snapshot_id = serializers.IntegerField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Structured error response"""
    status = serializers.CharField(default="error")
    message = serializers.CharField()
    code = serializers.CharField()
    details = serializers.JSONField(required=False)


# ===== STUDENT RESULT SERIALIZERS =====

class StudentResultSerializer(serializers.ModelSerializer):
    """Basic student result serializer"""
    class Meta:
        model = StudentResult
        fields = [
            "id",
            "reg_no",
            "stream",
            "section",
            "percentage",
            "grand_total",
            "result_class",
            "data_completeness_score",
            "percentage_was_filled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "result_class", "created_at", "updated_at"]


class TopperSerializer(serializers.Serializer):
    """
    STANDARDIZED Serializer for topper data
    
    Enforces consistent format across all topper types (college, stream).
    - Ensures percentage is always float
    - Maps field names to frontend expectations
    - Handles null values gracefully
    - Validates percentage range
    """
    rank = serializers.IntegerField(required=False, allow_null=True)
    reg_no = serializers.CharField()
    student_name = serializers.CharField(allow_blank=True, allow_null=True, default='N/A')
    stream = serializers.CharField(allow_blank=True, allow_null=True)
    section = serializers.CharField(allow_blank=True, allow_null=True)
    language = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    marks = serializers.FloatField(required=False, allow_null=True)  # grand_total
    percentage = serializers.FloatField()
    class_name = serializers.CharField(source='result_class', allow_blank=True)
    subject_marks = serializers.JSONField(required=False, allow_null=True)
    
    def validate_percentage(self, value):
        """Ensure percentage is numeric and in valid range"""
        if value is None:
            return value
        try:
            pct = float(value)
            if pct < 0 or pct > 100:
                raise serializers.ValidationError(
                    f"Percentage must be between 0 and 100, got {pct}"
                )
            return round(pct, 2)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                f"Percentage must be numeric, got {type(value).__name__}"
            )
    
    def validate_stream(self, value):
        """Normalize stream values"""
        if not value:
            return None
        normalized = str(value).upper().strip()
        valid = ['SCIENCE', 'COMMERCE']
        if normalized not in valid:
            # Log warning but don't fail
            print(f"⚠️ Invalid stream value: {value}, defaulting to None")
            return None
        return normalized


class SectionTopperSerializer(serializers.Serializer):
    """
    Serializer for section-wise topper data
    
    Section toppers do NOT have rank since they're per-section.
    Only includes essential fields.
    """
    reg_no = serializers.CharField()
    student_name = serializers.CharField(allow_blank=True, allow_null=True, default='N/A')
    percentage = serializers.FloatField()
    class_name = serializers.CharField(source='result_class', allow_blank=True)
    
    def validate_percentage(self, value):
        """Ensure percentage is numeric and in valid range"""
        if value is None:
            return value
        try:
            pct = float(value)
            if pct < 0 or pct > 100:
                raise serializers.ValidationError(
                    f"Percentage must be between 0 and 100, got {pct}"
                )
            return round(pct, 2)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                f"Percentage must be numeric, got {type(value).__name__}"
            )


class ToppersSerializer(serializers.Serializer):
    """Serializer for topper data"""
    rank = serializers.IntegerField()
    reg_no = serializers.CharField()
    stream = serializers.CharField()
    section = serializers.CharField(required=False, allow_null=True)
    grand_total = serializers.FloatField()
    percentage = serializers.FloatField()
    result_class = serializers.CharField()


class SectionPerformanceSerializer(serializers.Serializer):
    """Serializer for section performance data"""
    section = serializers.CharField()
    total_students = serializers.IntegerField()
    average_marks = serializers.FloatField()
    grade_distribution = serializers.JSONField()
    performance_indicators = serializers.JSONField(required=False)


class SubjectAnalysisSerializer(serializers.Serializer):
    """Serializer for subject analysis"""
    subject = serializers.CharField()
    total_students = serializers.IntegerField()
    average_score = serializers.FloatField()
    max_score = serializers.FloatField()
    min_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    grade_distribution = serializers.JSONField(required=False)


# ===== UPLOAD & QUALITY SERIALIZERS =====

# ===== STUDENT PERFORMANCE TABLE SERIALIZER =====

class StudentPerformanceTableSerializer(serializers.Serializer):
    """
    Serializer for Student Performance Table API
    
    Returns individual student data with subject-wise marks, totals, and classification.
    Designed for pagination and filtering in the frontend table component.
    """
    id = serializers.IntegerField()
    reg_no = serializers.CharField()
    name = serializers.CharField(source='student_name', allow_blank=True)
    section = serializers.CharField(allow_blank=True, allow_null=True)
    stream = serializers.CharField()
    subjects = serializers.SerializerMethodField()
    total = serializers.FloatField(source='grand_total')
    percentage = serializers.FloatField()
    result_class = serializers.CharField()
    
    def get_subjects(self, obj):
        """Extract subject marks from JSON field, handle missing marks"""
        subject_marks = obj.subject_marks_data or {}
        # Return dict with all subjects; missing ones are shown as None in frontend
        return {k: v if v is not None else None for k, v in subject_marks.items()}


class UploadLogSerializer(serializers.ModelSerializer):
    quality_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadLog
        fields = [
            "id",
            "filename",
            "status",
            "records_processed",
            "records_kept",
            "retention_rate",
            "quality_metrics",
            "error_message",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]
    
    def get_quality_metrics(self, obj):
        """Aggregate quality metrics for the upload"""
        return {
            "invalid_registration_numbers": obj.invalid_reg_no_removed,
            "duplicates_removed": obj.duplicates_removed,
            "missing_grand_total": obj.missing_grand_total_removed,
            "missing_percentage_filled": obj.missing_percentage_filled,
            "invalid_percentage_corrected": obj.invalid_percentage_corrected,
            "retention_rate": obj.retention_rate,
        }


class UploadResponseSerializer(serializers.Serializer):
    """Strict upload response format"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    records_processed = serializers.IntegerField()
    records_created = serializers.IntegerField()
    quality_report = serializers.JSONField()
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    versions = VersionInfoSerializer()


# ===== ANALYTICS SNAPSHOT SERIALIZERS =====

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for analytics snapshots"""
    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "id",
            "upload_log",
            "scope",
            "scope_value",
            "analytics_data",
            "analytics_version",
            "is_valid",
            "computed_at",
            "expires_at",
            "record_count",
            "computation_time_ms",
        ]
        read_only_fields = ["id", "computed_at"]


class AnalyticsResponseSerializer(serializers.Serializer):
    """Complete analytics response with all metadata"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    
    # Core analytics data
    summary = serializers.JSONField()
    toppers = ToppersSerializer(many=True)
    sections = SectionPerformanceSerializer(many=True)
    subjects = SubjectAnalysisSerializer(many=True)
    insights = serializers.JSONField(required=False)
    
    # Metadata
    versions = VersionInfoSerializer()
    cache_info = CacheInfoSerializer()
    record_count = serializers.IntegerField()
    generated_at = serializers.DateTimeField()


class ToppersResponseSerializer(serializers.Serializer):
    """Response for /toppers endpoint"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    toppers = ToppersSerializer(many=True)
    total_records = serializers.IntegerField()
    versions = VersionInfoSerializer()
    cache_info = CacheInfoSerializer()


class SectionsResponseSerializer(serializers.Serializer):
    """Response for /sections endpoint"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    sections = SectionPerformanceSerializer(many=True)
    total_sections = serializers.IntegerField()
    versions = VersionInfoSerializer()
    cache_info = CacheInfoSerializer()


class SubjectsResponseSerializer(serializers.Serializer):
    """Response for /subjects endpoint"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    subjects = SubjectAnalysisSerializer(many=True)
    total_subjects = serializers.IntegerField()
    versions = VersionInfoSerializer()
    cache_info = CacheInfoSerializer()


class ExportResponseSerializer(serializers.Serializer):
    """Response metadata for export endpoints"""
    status = serializers.CharField()
    upload_id = serializers.IntegerField()
    export_format = serializers.CharField()
    file_size_bytes = serializers.IntegerField()
    generated_at = serializers.DateTimeField()
    expires_in_seconds = serializers.IntegerField(required=False)


# ===== SECTION DATA TRANSFORMATION SERIALIZERS =====

class SectionDataSerializer(serializers.Serializer):
    """
    Serializer for transformed section data.
    
    Validates and serializes section performance metrics from row-based Excel data.
    
    Schema:
    - section: Section name (e.g., "PCMB A")
    - stream: "Science" or "Commerce"
    - enrolled: Total enrolled count (int)
    - absent: Total absent count (int)
    - appeared: Total appeared count (int)
    - distinction: Students with distinction (int)
    - first_class: Students with first class (int)
    - second_class: Students with second class (int)
    - pass_class: Students with pass class (int)
    - detained: Students detained (int)
    - promoted: Students promoted (int)
    - pass_percentage: Pass percentage (float, 0-100)
    """
    section = serializers.CharField(
        help_text="Section name (e.g., PCMB A)"
    )
    stream = serializers.ChoiceField(
        choices=["Science", "Commerce"],
        help_text="Stream assignment based on section"
    )
    enrolled = serializers.IntegerField(
        min_value=0,
        help_text="Total enrolled students"
    )
    absent = serializers.IntegerField(
        min_value=0,
        help_text="Total absent students"
    )
    appeared = serializers.IntegerField(
        min_value=0,
        help_text="Total appeared students"
    )
    distinction = serializers.IntegerField(
        min_value=0,
        help_text="Students with distinction"
    )
    first_class = serializers.IntegerField(
        min_value=0,
        help_text="Students with first class"
    )
    second_class = serializers.IntegerField(
        min_value=0,
        help_text="Students with second class"
    )
    pass_class = serializers.IntegerField(
        min_value=0,
        help_text="Students with pass class"
    )
    detained = serializers.IntegerField(
        min_value=0,
        help_text="Students detained"
    )
    promoted = serializers.IntegerField(
        min_value=0,
        help_text="Students promoted"
    )
    pass_percentage = serializers.FloatField(
        min_value=0.0,
        max_value=100.0,
        help_text="Pass percentage (0-100)"
    )
    
    def validate(self, data):
        """Validate data consistency"""
        # Check that class counts don't exceed appeared
        class_total = (
            data['distinction'] + data['first_class'] +
            data['second_class'] + data['pass_class']
        )
        if class_total > data['appeared']:
            raise serializers.ValidationError(
                f"Sum of classes ({class_total}) cannot exceed appeared ({data['appeared']})"
            )
        
        return data


class SectionDataResponseSerializer(serializers.Serializer):
    """Response format for section data transformation"""
    status = serializers.CharField(
        default="success",
        help_text="Response status (success/error)"
    )
    data = SectionDataSerializer(many=True, help_text="Array of 12 section objects")
    count = serializers.IntegerField(help_text="Number of sections (must be 12)")
    errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of validation errors (empty if success)"
    )
    validation_summary = serializers.JSONField(
        required=False,
        help_text="Summary of validation results"
    )
