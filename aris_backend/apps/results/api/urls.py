"""
STRICT API ROUTING

All endpoints serve from precomputed snapshots.
Endpoints follow RESTful conventions and include versioning.

UPLOAD FLOW:
  POST /api/upload/ → Process → Cache

ANALYTICS FLOW:
  GET /api/analytics/{upload_id}/ → Snapshot
  GET /api/toppers/{upload_id}/ → Toppers from Snapshot
  GET /api/sections/{upload_id}/ → Sections from Snapshot
  GET /api/subjects/{upload_id}/ → Subjects from Snapshot

SECTION PERFORMANCE (NEW):
  POST /api/sections/transform/ → Transform row-based metrics to sections
  GET /api/sections/sample/ → Get sample data and transformation

STUDENT PERFORMANCE TABLE (NEW):
  GET /api/students/ → List students with filtering, pagination, and subject marks

EXPORT FLOW:
  GET /api/export/excel/{upload_id}/ → Excel file

LEGACY (Backward Compatible):
  GET /api/analytics/ → Global analytics
  GET /api/analytics/stream/?stream=SCIENCE → Stream analytics
  GET /api/analytics/section/?section=A → Section analytics
  GET /api/analytics/upload/{upload_id}/ → Upload analytics
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from apps.results.api import views
from apps.results.api.section_views import SectionTransformView, SectionSampleDataView
from apps.results.api.heatmap_views import HeatmapDataView, HeatmapSampleView

urlpatterns = [
    # ===== CSRF (SECURITY) =====
    path("csrf/", csrf_exempt(views.CsrfTokenView.as_view()), name="csrf"),
    
    # ===== UPLOAD (ENTRY POINT) =====
    path("upload/", csrf_exempt(views.UploadView.as_view()), name="upload"),
    
    # ===== STUDENT PERFORMANCE TABLE (NEW) =====
    path("students/", views.StudentPerformanceView.as_view(), name="students"),
    
    # ===== SECTION PERFORMANCE TRANSFORMATION (NEW) =====
    path("sections/transform/", SectionTransformView.as_view(), name="section-transform"),
    path("sections/sample/", SectionSampleDataView.as_view(), name="section-sample"),
    
    # ===== HEATMAP DATA (SECTION × SUBJECT ANALYSIS) =====
    path("heatmap/", HeatmapDataView.as_view(), name="heatmap"),
    path("heatmap/sample/", HeatmapSampleView.as_view(), name="heatmap-sample"),
    
    # ===== ANALYTICS ENDPOINTS (NEW) =====
    path("analytics/<int:upload_id>/", views.AnalyticsView.as_view(), name="analytics-detail"),
    path("toppers/<int:upload_id>/", views.ToppersView.as_view(), name="toppers"),
    path("toppers/section/<int:upload_id>/", views.SectionToppersView.as_view(), name="toppers-section"),
    path("sections/<int:upload_id>/", views.SectionsView.as_view(), name="sections"),
    path("subjects/<int:upload_id>/", views.SubjectsView.as_view(), name="subjects"),
    
    # ===== EXCEL EXPORT (NEW) =====
    path("export/excel/<int:upload_id>/", views.ExcelExportView.as_view(), name="export-excel"),
    
    # ===== LEGACY ENDPOINTS (Backward Compatibility) =====
    # Results
    path("results/", views.ResultDetailView.as_view(), name="results-list"),
    path("results/<str:reg_no>/", views.ResultDetailView.as_view(), name="result-detail"),
    
    # Upload history
    path("uploads/", views.UploadHistoryView.as_view(), name="upload-history"),
    
    # Statistics
    path("stats/", views.StatsView.as_view(), name="stats"),
    
    # Legacy Analytics (Global/Stream/Section scoped)
    path("analytics/", views.AnalyticsView.as_view(), name="analytics-global"),
    path("analytics/upload/<int:upload_id>/", views.UploadAnalyticsView.as_view(), name="upload-analytics-legacy"),
    path("analytics/section/", views.SectionAnalyticsView.as_view(), name="section-analytics-legacy"),
    path("analytics/stream/", views.StreamAnalyticsView.as_view(), name="stream-analytics-legacy"),
]

