"""
STRICT API AND OUTPUT ENGINE

This is the API layer that serves analytics data from precomputed snapshots.
Each endpoint implements:
- Snapshot-only serving (NO recomputation)
- Standard versioning in responses
- Performance tracking
- Strict error handling
- CORS compatibility for Vite frontend

CORE PRINCIPLE: NEVER recompute analytics in the API layer.
Always fetch from AnalyticsSnapshot cache and return in <1 second.
"""

import time
from io import BytesIO
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apps.results.models import StudentResult, UploadLog, AnalyticsSnapshot
from apps.results.api.serializers import (
    StudentResultSerializer,
    UploadLogSerializer,
    StudentPerformanceTableSerializer,
)
from apps.results.services.analyzer import process_upload
from apps.results.services.analytics import compute_analytics
from apps.results.services.snapshot import SnapshotManager
from apps.results.services.excel_exporter import ExcelExporter
from apps.results.utils import validate_file_size, validate_file_extension
from apps.results.api.api_utils import (
    track_performance,
    get_version_info,
    get_cache_info,
    build_error_response,
    safe_snapshot_fetch,
    APIError,
    INVALID_FILE,
    ANALYTICS_NOT_FOUND,
    EXPORT_FAILED,
    UPLOAD_NOT_FOUND,
)



# ===== CSRF ENDPOINT =====

class CsrfTokenView(APIView):
    """
    GET /api/csrf/
    
    Returns CSRF token for cross-origin requests
    """
    
    def get(self, request):
        """Get CSRF token - simple endpoint that just returns success"""
        try:
            from django.middleware.csrf import get_token
            csrf_token = get_token(request)
            return Response({
                "csrfToken": csrf_token,
                "status": "success"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Even if CSRF token fails, return something
            return Response({
                "status": "success",
                "csrfToken": "not-needed-for-api",
                "message": "CSRF tokens not needed for JWT API"
            }, status=status.HTTP_200_OK)


# ===== UPLOAD ENDPOINT =====

class UploadView(APIView):
    """
    POST /api/upload/
    
    ENTRY POINT: Accept Excel file → Clean → Analyze → Cache
    
    Flow:
    1. Validate file (size, format)
    2. Pass to PART 1 (Data Cleaning)
    3. Validate cleaned data (Contract + Gate)
    4. Store in StudentResult
    5. Pass to PART 2 (Analytics)
    6. Generate and cache snapshot
    7. Return response with versions
    """

    parser_classes = (MultiPartParser, FormParser)

    @track_performance
    def post(self, request):
        """Upload Excel and process through full pipeline"""
        try:
            file = request.FILES.get("file")

            # Validate file exists
            if not file:
                return build_error_response(
                    APIError("No file uploaded", code="MISSING_FILE", status_code=status.HTTP_400_BAD_REQUEST)
                )

            # Validate file size
            is_valid, error = validate_file_size(file)
            if not is_valid:
                return build_error_response(
                    INVALID_FILE(details={"reason": error})
                )

            # Validate file extension
            is_valid, error = validate_file_extension(file)
            if not is_valid:
                return build_error_response(
                    INVALID_FILE(details={"reason": error})
                )

            # Create upload log
            upload_log = UploadLog.objects.create(
                filename=file.name,
                status="PENDING"
            )

            # Process upload through PART 1 + PART 2
            success, records_created, quality_metrics, error_msg = process_upload(file, upload_log)

            if success:
                upload_log.status = "SUCCESS"
                upload_log.save()

                # Build response with versions
                response_data = {
                    "status": "success",
                    "upload_id": upload_log.id,
                    "records_processed": upload_log.records_processed,
                    "records_created": records_created,
                    "quality_report": {
                        "data_quality": {
                            "retention_rate": quality_metrics.get("retention_rate", 0),
                            "original_records": quality_metrics.get("original_records", 0),
                            "final_records": quality_metrics.get("final_records", 0),
                        },
                        "issues_found": {
                            "invalid_registration_numbers": quality_metrics.get("invalid_reg_no_removed", 0),
                            "duplicates_removed": quality_metrics.get("duplicates_removed", 0),
                            "upload_duplicates_cleaned": quality_metrics.get("upload_duplicates_removed", 0),
                            "database_duplicates_cleaned": quality_metrics.get("db_duplicates_removed", 0),
                            "missing_grand_total": quality_metrics.get("missing_grand_total_removed", 0),
                            "missing_percentage_filled": quality_metrics.get("missing_percentage_filled", 0),
                            "invalid_percentage_corrected": quality_metrics.get("invalid_percentage_corrected", 0),
                            "section_mismatches": quality_metrics.get("section_mismatches", 0),
                            "total_mismatches": quality_metrics.get("total_mismatches", 0),
                            "percentage_mismatches": quality_metrics.get("percentage_mismatches", 0),
                        },
                    },
                    "versions": get_version_info(upload_log=upload_log),
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                upload_log.status = "FAILED"
                upload_log.error_message = error_msg
                upload_log.save()

                return build_error_response(
                    APIError(error_msg, code="UPLOAD_PROCESSING_FAILED", status_code=status.HTTP_400_BAD_REQUEST,
                            details={"upload_id": upload_log.id, "quality_metrics": quality_metrics})
                )

        except Exception as e:
            return build_error_response(
                APIError(f"Upload processing error: {str(e)}", code="UPLOAD_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )



# ===== ANALYTICS ENDPOINTS =====

class ToppersView(APIView):
    """
    GET /api/toppers/{upload_id}/
    
    Returns: Top 10 students by category (college, science, commerce)
    
    Source: AnalyticsSnapshot (NEVER recomputed)
    Format: Standardized, cleaned topper data
    """

    @track_performance
    def get(self, request, upload_id):
        """Fetch toppers from cached snapshot (college, science, commerce)"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Fetch snapshot (NEVER recompute)
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Extract toppers from snapshot
            analytics_data = snapshot.analytics_data
            toppers_data = analytics_data.get("toppers", {})
            
            # Get toppers by category (top 10 each, cleaned format)
            college_toppers = toppers_data.get("college", [])[:10]
            science_toppers = toppers_data.get("science", [])[:10]
            commerce_toppers = toppers_data.get("commerce", [])[:10]

            response_time_ms = int((time.time() - start_time) * 1000)

            return Response({
                "status": "success",
                "upload_id": upload_id,
                "data": {
                    "toppers": {
                        "college": college_toppers,
                        "science": science_toppers,
                        "commerce": commerce_toppers
                    }
                },
                "total_records": snapshot.record_count,
                "versions": get_version_info(upload_log=upload_log, analytics_snapshot=snapshot),
                "cache_info": get_cache_info(
                    was_cached=True,
                    response_time_ms=response_time_ms,
                    snapshot=snapshot,
                    cached_at=snapshot.computed_at,
                    expires_at=snapshot.expires_at
                )
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch toppers: {str(e)}", code="TOPPERS_FETCH_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class SectionToppersView(APIView):
    """
    GET /api/toppers/section/{upload_id}/
    
    Returns: Top 10 students per section
    
    Source: AnalyticsSnapshot (NEVER recomputed)
    Format: Section-based topper data without rank
    """

    @track_performance
    def get(self, request, upload_id):
        """Fetch section-wise toppers from cached snapshot"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Fetch snapshot (NEVER recompute)
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Extract section toppers from snapshot
            analytics_data = snapshot.analytics_data
            toppers_data = analytics_data.get("toppers", {})
            
            # Extract all section_X entries
            section_toppers = {}
            for key, value in toppers_data.items():
                if key.startswith("section_"):
                    # Clean section name and limit to top 10
                    section_name = key.replace("section_", "")
                    section_toppers[section_name] = value[:10]

            response_time_ms = int((time.time() - start_time) * 1000)

            return Response({
                "status": "success",
                "upload_id": upload_id,
                "data": {
                    "toppers": section_toppers
                },
                "total_sections": len(section_toppers),
                "total_records": snapshot.record_count,
                "versions": get_version_info(upload_log=upload_log, analytics_snapshot=snapshot),
                "cache_info": get_cache_info(
                    was_cached=True,
                    response_time_ms=response_time_ms,
                    snapshot=snapshot,
                    cached_at=snapshot.computed_at,
                    expires_at=snapshot.expires_at
                )
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch section toppers: {str(e)}", code="SECTION_TOPPERS_FETCH_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class SectionsView(APIView):
    """
    GET /api/sections/{upload_id}/
    
    Returns: Section-wise performance breakdown
    
    Source: AnalyticsSnapshot (NEVER recomputed)
    """

    @track_performance
    def get(self, request, upload_id):
        """Fetch section performance from cached snapshot"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Fetch snapshot
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Extract sections from snapshot
            analytics_data = snapshot.analytics_data
            # Current analytics schema uses "sections" (list of metrics dicts).
            # Keep backward compatibility for older snapshots that used "section_summary".
            sections = (
                analytics_data.get("sections")
                or analytics_data.get("section_summary")
                or []
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return Response({
                "status": "success",
                "upload_id": upload_id,
                "sections": sections,
                "total_sections": len(sections) if hasattr(sections, "__len__") else 0,
                "versions": get_version_info(upload_log=upload_log, analytics_snapshot=snapshot),
                "cache_info": get_cache_info(
                    was_cached=True,
                    response_time_ms=response_time_ms,
                    snapshot=snapshot,
                    cached_at=snapshot.computed_at,
                    expires_at=snapshot.expires_at
                )
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch sections: {str(e)}", code="SECTIONS_FETCH_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class SubjectsView(APIView):
    """
    GET /api/subjects/{upload_id}/
    
    Returns: Subject-wise analysis (avg score, pass rate, etc)
    
    Source: AnalyticsSnapshot (NEVER recomputed)
    """

    @track_performance
    def get(self, request, upload_id):
        """Fetch subject analysis from cached snapshot"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Fetch snapshot
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Extract subjects from snapshot
            analytics_data = snapshot.analytics_data
            # Current analytics schema uses "subjects" (dict). Keep backward compatibility.
            subjects = (
                analytics_data.get("subjects")
                or analytics_data.get("subject_analysis")
                or {}
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return Response({
                "status": "success",
                "upload_id": upload_id,
                "subjects": subjects,
                "total_subjects": len(subjects),
                "versions": get_version_info(upload_log=upload_log, analytics_snapshot=snapshot),
                "cache_info": get_cache_info(
                    was_cached=True,
                    response_time_ms=response_time_ms,
                    snapshot=snapshot,
                    cached_at=snapshot.computed_at,
                    expires_at=snapshot.expires_at
                )
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch subjects: {str(e)}", code="SUBJECTS_FETCH_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class AnalyticsView(APIView):
    """
    GET /api/analytics/{upload_id}/
    
    Returns: COMPLETE analytics (toppers + sections + subjects + summary)
    
    Source: AnalyticsSnapshot (NEVER recomputed)
    """

    @track_performance
    def get(self, request, upload_id):
        """Fetch complete analytics from cached snapshot"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Fetch snapshot
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Return complete analytics snapshot
            response_time_ms = int((time.time() - start_time) * 1000)

            return Response({
                "status": "success",
                "upload_id": upload_id,
                "analytics": snapshot.analytics_data,
                "versions": get_version_info(upload_log=upload_log, analytics_snapshot=snapshot),
                "cache_info": get_cache_info(
                    was_cached=True,
                    response_time_ms=response_time_ms,
                    snapshot=snapshot,
                    cached_at=snapshot.computed_at,
                    expires_at=snapshot.expires_at
                )
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch analytics: {str(e)}", code="ANALYTICS_FETCH_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


# ===== EXCEL EXPORT ENDPOINT =====

class ExcelExportView(APIView):
    """
    GET /api/export/excel/{upload_id}/
    
    Generates presentation-ready Excel with 5 sheets:
    1. College Toppers
    2. Science Toppers
    3. Commerce Toppers
    4. Section Performance
    5. Subject Analysis
    
    All data sourced from AnalyticsSnapshot (NEVER recomputed)
    """

    @track_performance
    def get(self, request, upload_id):
        """Generate Excel export from cached analytics"""
        try:
            start_time = time.time()

            # Validate upload exists
            try:
                upload_log = UploadLog.objects.get(id=upload_id)
            except UploadLog.DoesNotExist:
                return build_error_response(UPLOAD_NOT_FOUND(upload_id))

            # Verify analytics exists BEFORE attempting export
            snapshot, error = safe_snapshot_fetch(upload_id, scope="UPLOAD")
            if error:
                return build_error_response(error)

            # Generate Excel from snapshot
            try:
                excel_file = ExcelExporter.generate_export(upload_id)
                file_size = excel_file.getbuffer().nbytes
                response_time_ms = int((time.time() - start_time) * 1000)

                # Return file as attachment
                response = FileResponse(
                    excel_file,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    status=status.HTTP_200_OK
                )
                response['Content-Disposition'] = f'attachment; filename="ARIS_Analytics_{upload_id}.xlsx"'
                response['X-File-Size'] = file_size
                response['X-Response-Time-Ms'] = response_time_ms

                return response

            except Exception as e:
                return build_error_response(
                    EXPORT_FAILED(str(e), details={"upload_id": upload_id})
                )

        except Exception as e:
            return build_error_response(
                APIError(f"Excel export error: {str(e)}", code="EXPORT_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


    """Get all student results with filtering"""

    def get(self, request):
        """Fetch all results with optional filtering"""
        queryset = StudentResult.objects.all()

        # Filter by stream
        stream = request.query_params.get("stream")
        if stream:
            queryset = queryset.filter(stream=stream)

        # Filter by section
        section = request.query_params.get("section")
        if section:
            queryset = queryset.filter(section=section)

        # Search by registration number
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(reg_no__icontains=search)

        # Ordering
        ordering = request.query_params.get("ordering", "-grand_total")
        queryset = queryset.order_by(ordering)

        # Pagination
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 100)
        
        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page, page_size = 1, 100

        start = (page - 1) * page_size
        end = start + page_size

        serializer = StudentResultSerializer(queryset[start:end], many=True)
        
        return Response({
            "count": queryset.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        }, status=status.HTTP_200_OK)


class ResultDetailView(APIView):
    """Get a single student result"""

    def get(self, request, reg_no):
        """Fetch a single result by registration number"""
        try:
            result = StudentResult.objects.get(reg_no=reg_no)
            serializer = StudentResultSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentResult.DoesNotExist:
            return Response(
                {"error": "Result not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UploadHistoryView(APIView):
    """Get upload history and logs"""

    def get(self, request):
        """Fetch all upload logs"""
        logs = UploadLog.objects.all().order_by("-uploaded_at")
        serializer = UploadLogSerializer(logs, many=True)
        return Response({
            "status": "success",
            "data": serializer.data,
            "count": logs.count()
        }, status=status.HTTP_200_OK)


class StatsView(APIView):
    """Get statistics about the results"""

    def get(self, request):
        """Get aggregate statistics"""
        total_records = StudentResult.objects.count()
        
        stats_by_stream = {}
        for stream in ["SCIENCE", "COMMERCE"]:
            count = StudentResult.objects.filter(stream=stream).count()
            avg_total = StudentResult.objects.filter(stream=stream)\
                .values_list("grand_total", flat=True).__iter__()
            
            totals = list(StudentResult.objects.filter(stream=stream)\
                .values_list("grand_total", flat=True))
            
            avg_total = sum(totals) / len(totals) if totals else 0
            
            stats_by_stream[stream] = {
                "count": count,
                "average_total": round(avg_total, 2)
            }

        return Response({
            "total_records": total_records,
            "by_stream": stats_by_stream
        }, status=status.HTTP_200_OK)


class GlobalAnalyticsView(APIView):
    """
    Strict Analytics Engine - Complete institutional analytics
    
    PRODUCTION: Uses snapshot caching for fast response (<100ms)
    
    Returns:
    - Global summary (pass %, distinctions, etc)
    - College toppers (Top 10 overall)
    - Stream-wise toppers (Science, Commerce)
    - Section-wise toppers (Top 10 per section)
    - Section performance metrics
    - Subject-wise analysis with grade distribution
    - Data insights (highest section, top student, etc)
    """

    def get(self, request):
        """Generate complete analytics from clean data (or return cached snapshot)"""
        from apps.results.services.snapshot import SnapshotManager
        import time
        
        start_time = time.time()
        
        # Try to get from cache
        cached_snapshot = SnapshotManager.get_cached_analytics(
            scope="GLOBAL",
            scope_value=None,
        )
        
        if cached_snapshot:
            # Return cached analytics (<50ms)
            response_time_ms = int((time.time() - start_time) * 1000)
            cached_snapshot.analytics_data['_cache_info'] = {
                'was_cached': True,
                'response_time_ms': response_time_ms,
                'cached_at': cached_snapshot.computed_at.isoformat(),
            }
            return Response(
                cached_snapshot.analytics_data,
                status=status.HTTP_200_OK
            )
        
        # No cache: compute analytics
        analytics = compute_analytics(StudentResult.objects.all())
        
        response_time_ms = int((time.time() - start_time) * 1000)
        analytics['_cache_info'] = {
            'was_cached': False,
            'response_time_ms': response_time_ms,
        }
        
        http_status = status.HTTP_200_OK if analytics['status'] == 'success' else status.HTTP_400_BAD_REQUEST
        
        return Response(analytics, status=http_status)


class UploadAnalyticsView(APIView):
    """Analytics for a specific upload (immutable snapshot)"""

    def get(self, request, upload_id):
        """Get analytics for specific upload (always cached after upload)"""
        from apps.results.services.snapshot import SnapshotManager
        import time
        
        start_time = time.time()
        
        try:
            upload_log = UploadLog.objects.get(id=upload_id)
            
            # Try to get from cache (upload snapshots don't expire)
            cached_snapshot = SnapshotManager.get_cached_analytics(
                scope="UPLOAD",
                scope_value=str(upload_id),
                upload_log=upload_log,
            )
            
            if cached_snapshot:
                # Return cached analytics
                response_time_ms = int((time.time() - start_time) * 1000)
                cached_snapshot.analytics_data['_cache_info'] = {
                    'was_cached': True,
                    'response_time_ms': response_time_ms,
                    'cached_at': cached_snapshot.computed_at.isoformat(),
                }
                return Response(
                    cached_snapshot.analytics_data,
                    status=status.HTTP_200_OK
                )
            
            # No cache: compute and cache
            queryset = StudentResult.objects.filter(upload_log=upload_log)
            analytics = compute_analytics(queryset)
            
            # Add upload metadata
            analytics['upload_metadata'] = {
                'upload_id': upload_log.id,
                'filename': upload_log.filename,
                'uploaded_at': upload_log.uploaded_at.isoformat(),
                'status': upload_log.status,
                'retention_rate': round(upload_log.retention_rate, 2),
                'quality_metrics': {
                    'records_processed': upload_log.records_processed,
                    'records_kept': upload_log.records_kept,
                    'section_mismatches': upload_log.section_mismatches,
                    'total_mismatches': upload_log.total_mismatches,
                    'percentage_mismatches': upload_log.percentage_mismatches,
                    'alternate_identifiers_found': upload_log.alternate_identifiers_found,
                }
            }
            
            response_time_ms = int((time.time() - start_time) * 1000)
            analytics['_cache_info'] = {
                'was_cached': False,
                'response_time_ms': response_time_ms,
            }
            
            http_status = status.HTTP_200_OK if analytics['status'] == 'success' else status.HTTP_400_BAD_REQUEST
            
            return Response(analytics, status=http_status)
            
        except UploadLog.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Upload {upload_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)


class SectionAnalyticsView(APIView):
    """Analytics for specific section(s) - cached"""

    def get(self, request):
        """Get analytics for specific section or all sections"""
        from apps.results.services.snapshot import SnapshotManager
        import time
        
        start_time = time.time()
        
        section = request.query_params.get("section")
        
        if section:
            # Try cache for specific section
            cached_snapshot = SnapshotManager.get_cached_analytics(
                scope="SECTION",
                scope_value=section,
            )
            
            if cached_snapshot:
                response_time_ms = int((time.time() - start_time) * 1000)
                cached_snapshot.analytics_data['_cache_info'] = {
                    'was_cached': True,
                    'response_time_ms': response_time_ms,
                    'cached_at': cached_snapshot.computed_at.isoformat(),
                }
                return Response(
                    cached_snapshot.analytics_data,
                    status=status.HTTP_200_OK
                )
            
            queryset = StudentResult.objects.filter(section=section)
        else:
            # Try cache for all sections (global)
            cached_snapshot = SnapshotManager.get_cached_analytics(
                scope="GLOBAL",
                scope_value=None,
            )
            
            if cached_snapshot:
                response_time_ms = int((time.time() - start_time) * 1000)
                cached_snapshot.analytics_data['_cache_info'] = {
                    'was_cached': True,
                    'response_time_ms': response_time_ms,
                    'cached_at': cached_snapshot.computed_at.isoformat(),
                }
                return Response(
                    cached_snapshot.analytics_data,
                    status=status.HTTP_200_OK
                )
            
            queryset = StudentResult.objects.all()
        
        # Generate analytics (if not in cache)
        analytics = compute_analytics(queryset)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        analytics['_cache_info'] = {
            'was_cached': False,
            'response_time_ms': response_time_ms,
        }
        
        http_status = status.HTTP_200_OK if analytics['status'] == 'success' else status.HTTP_400_BAD_REQUEST
        
        return Response(analytics, status=http_status)


class StreamAnalyticsView(APIView):
    """Analytics for specific stream (SCIENCE/COMMERCE) - cached"""

    def get(self, request):
        """Get analytics for specific stream"""
        from apps.results.services.snapshot import SnapshotManager
        import time
        
        start_time = time.time()
        
        stream = request.query_params.get("stream", "").upper()
        
        if stream not in ['SCIENCE', 'COMMERCE']:
            return Response({
                "status": "error",
                "message": "Stream must be SCIENCE or COMMERCE"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try cache
        cached_snapshot = SnapshotManager.get_cached_analytics(
            scope="STREAM",
            scope_value=stream,
        )
        
        if cached_snapshot:
            response_time_ms = int((time.time() - start_time) * 1000)
            cached_snapshot.analytics_data['_cache_info'] = {
                'was_cached': True,
                'response_time_ms': response_time_ms,
                'cached_at': cached_snapshot.computed_at.isoformat(),
            }
            return Response(
                cached_snapshot.analytics_data,
                status=status.HTTP_200_OK
            )
        
        # Generate analytics
        queryset = StudentResult.objects.filter(stream=stream)
        
        # Generate analytics
        analytics = compute_analytics(queryset)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        analytics['_cache_info'] = {
            'was_cached': False,
            'response_time_ms': response_time_ms,
        }
        
        http_status = status.HTTP_200_OK if analytics['status'] == 'success' else status.HTTP_400_BAD_REQUEST
        
        return Response(analytics, status=http_status)


# ===== STUDENT PERFORMANCE TABLE =====

class StudentPerformanceView(APIView):
    """
    GET /api/students/
    
    Returns: Individual student data with subject-wise marks, totals, and classification.
    
    Query Parameters:
    - upload_id: Upload ID (filter students to a specific upload)
    - stream: SCIENCE/COMMERCE (filter by stream)
    - section: Section name (filter by section)
    - result_class: DISTINCTION/FIRST_CLASS/SECOND_CLASS/PASS/FAIL (filter by classification)
    - search: Student name (search by student name)
    - limit: Number of records per page (default: 50, max: 500)
    - offset: Pagination offset (default: 0)
    
    Response: Paginated list of students with their performance data
    """

    @track_performance
    def get(self, request):
        """Fetch student list with filtering and pagination"""
        try:
            start_time = time.time()
            
            # Get filter parameters
            upload_id = request.query_params.get('upload_id', '').strip()
            stream = request.query_params.get('stream', '').upper()
            section = request.query_params.get('section', '').strip()
            result_class = request.query_params.get('result_class', '').upper()
            search = request.query_params.get('search', '').strip()
            
            # Get pagination parameters
            limit = min(int(request.query_params.get('limit', 50)), 500)
            offset = int(request.query_params.get('offset', 0))
            
            # Build base queryset
            queryset = StudentResult.objects.all()

            if upload_id:
                queryset = queryset.filter(upload_log_id=upload_id)
            
            # Apply filters
            if stream and stream in ['SCIENCE', 'COMMERCE']:
                queryset = queryset.filter(stream=stream)
            
            if section:
                queryset = queryset.filter(section__icontains=section)
            
            if result_class and result_class in ['DISTINCTION', 'FIRST_CLASS', 'SECOND_CLASS', 'PASS', 'FAIL', 'INCOMPLETE']:
                queryset = queryset.filter(result_class=result_class)
            
            if search:
                queryset = queryset.filter(student_name__icontains=search)
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Apply pagination
            paginated_queryset = queryset.order_by('-grand_total')[offset:offset+limit]
            
            # Serialize data
            serializer = StudentPerformanceTableSerializer(paginated_queryset, many=True)
            
            # Get available sections and subjects for filter dropdowns
            section_qs = StudentResult.objects.all()
            if upload_id:
                section_qs = section_qs.filter(upload_log_id=upload_id)
            if stream:
                section_qs = section_qs.filter(stream=stream)
            all_sections = list(section_qs.values_list('section', flat=True).distinct().order_by('section'))
            
            # Get all possible result classes
            result_classes = ['DISTINCTION', 'FIRST_CLASS', 'SECOND_CLASS', 'PASS', 'FAIL']
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return Response({
                "status": "success",
                "data": serializer.data,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "returned": len(serializer.data),
                    "has_next": offset + limit < total_count
                },
                "filters": {
                    "streams": ['SCIENCE', 'COMMERCE'],
                    "sections": all_sections,
                    "result_classes": result_classes,
                    "active_filters": {
                        "upload_id": upload_id or None,
                        "stream": stream or None,
                        "section": section or None,
                        "result_class": result_class or None,
                        "search": search or None,
                    }
                },
                "cache_info": {
                    "was_cached": False,
                    "response_time_ms": response_time_ms,
                }
            }, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError) as e:
            return build_error_response(
                APIError(f"Invalid parameters: {str(e)}", code="INVALID_PARAMS", status_code=status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            return build_error_response(
                APIError(f"Failed to fetch students: {str(e)}", code="STUDENTS_FETCH_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )

