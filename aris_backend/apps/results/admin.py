from django.contrib import admin
from apps.results.models import StudentResult, UploadLog


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = (
        "reg_no",
        "stream",
        "section",
        "result_class",
        "grand_total",
        "percentage",
        "data_completeness_score",
        "created_at"
    )
    list_filter = ("stream", "section", "result_class", "created_at")
    search_fields = ("reg_no",)
    readonly_fields = ("result_class", "data_completeness_score", "created_at", "updated_at")
    ordering = ("-grand_total",)
    
    fieldsets = (
        ("Registration", {
            "fields": ("reg_no", "stream", "section")
        }),
        ("Scores", {
            "fields": ("grand_total", "percentage", "result_class")
        }),
        ("Data Quality", {
            "fields": ("data_completeness_score", "percentage_was_filled")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(UploadLog)
class UploadLogAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "status",
        "records_kept",
        "retention_rate",
        "duplicates_removed",
        "section_mismatches",
        "total_mismatches",
        "uploaded_at"
    )
    list_filter = ("status", "uploaded_at")
    search_fields = ("filename",)
    readonly_fields = (
        "uploaded_at",
        "invalid_reg_no_removed",
        "duplicates_removed",
        "missing_grand_total_removed",
        "missing_percentage_filled",
        "invalid_percentage_corrected",
        "section_mismatches",
        "total_mismatches",
        "percentage_mismatches",
        "alternate_identifiers_found",
    )
    
    fieldsets = (
        ("File Information", {
            "fields": ("filename", "status", "uploaded_at")
        }),
        ("Processing Stats", {
            "fields": ("records_processed", "records_kept", "retention_rate")
        }),
        ("Data Integrity Metrics", {
            "fields": (
                "invalid_reg_no_removed",
                "duplicates_removed",
                "missing_grand_total_removed",
                "missing_percentage_filled",
                "invalid_percentage_corrected",
            )
        }),
        ("Data Validation Warnings", {
            "fields": (
                "section_mismatches",
                "total_mismatches",
                "percentage_mismatches",
                "alternate_identifiers_found",
            ),
            "description": "These indicate potential data quality issues that should be reviewed"
        }),
        ("Error Details", {
            "fields": ("error_message",),
            "classes": ("collapse",)
        }),
    )
