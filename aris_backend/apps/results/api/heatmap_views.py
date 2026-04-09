"""
Heatmap Data API Views

Endpoints:
- POST /api/heatmap/: Transform raw metrics to heatmap records
- GET /api/heatmap/: Get heatmap data for specified section
- GET /api/heatmap/sample/: Get sample test data and transformation
"""

import time
import json
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.results.services.heatmap_transformer import HeatmapTransformer, HeatmapTransformationError
from apps.results.services.heatmap_test_data import get_heatmap_test_data
from apps.results.api.api_utils import build_error_response, APIError, track_performance


class HeatmapDataView(APIView):
    """
    POST /api/heatmap/: Transform section-subject metrics to heatmap
    GET /api/heatmap/?section=PCMB%20A: Get heatmap for specific section
    
    Input format (JSON):
    {
        "Distinction": {"PCMB A - MATHS": 22, "PCMB A - ENG": 20, ...},
        "First Class": {...},
        "Second Class": {...},
        "Pass Class": {...},
        "Fail": {...},
        "Total": {...}
    }
    
    Output format:
    [
        {
            "section": "PCMB A",
            "subject": "MATHS",
            "pass_percentage": 96.15,
            "fail": 0,
            "total": 52,
            "stream": "Science"
        }
    ]
    """
    
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    @track_performance
    def post(self, request):
        """Transform heatmap metrics from JSON or Excel"""
        try:
            start_time = time.time()
            
            # Check if file upload or JSON body
            if request.FILES:
                file = request.FILES.get('file')
                if not file:
                    return build_error_response(
                        APIError("No file uploaded", code="MISSING_FILE",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
                
                try:
                    excel_data = pd.read_excel(file)
                    # Set first column as index (metric names)
                    excel_data = excel_data.set_index(excel_data.columns[0])
                except Exception as e:
                    return build_error_response(
                        APIError(f"Failed to parse Excel file: {str(e)}",
                                code="PARSE_ERROR",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
            else:
                # JSON body
                if not request.data:
                    return build_error_response(
                        APIError("Empty request body", code="EMPTY_REQUEST",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
                
                # Convert dict to DataFrame
                json_data = request.data
                if isinstance(json_data, dict):
                    excel_data = pd.DataFrame(json_data).T
                else:
                    return build_error_response(
                        APIError("Request data must be a JSON object with metrics as keys",
                                code="INVALID_FORMAT",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
            
            # Transform
            transformer = HeatmapTransformer(excel_data)
            heatmap_records, errors = transformer.transform()
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return Response({
                'status': 'success' if len(errors) == 0 else 'success_with_warnings',
                'data': heatmap_records,
                'count': len(heatmap_records),
                'errors': errors,
                'response_time_ms': response_time_ms,
            }, status=status.HTTP_200_OK)
            
        except HeatmapTransformationError as e:
            return build_error_response(
                APIError(str(e), code="TRANSFORM_ERROR",
                        status_code=status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            print(f"❌ Exception in HeatmapDataView POST: {str(e)}")
            import traceback
            traceback.print_exc()
            return build_error_response(
                APIError(f"Heatmap transformation error: {str(e)}",
                        code="TRANSFORM_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
    
    @track_performance
    def get(self, request):
        """Get heatmap data for specified section or stream"""
        try:
            start_time = time.time()
            
            section = request.query_params.get('section')
            stream = request.query_params.get('stream')
            format_type = request.query_params.get('format', 'grade-distribution')  # New parameter
            
            if not section and not stream:
                return build_error_response(
                    APIError("Please specify section or stream query parameter",
                            code="MISSING_FILTER",
                            status_code=status.HTTP_400_BAD_REQUEST)
                )
            
            # Get appropriate test data based on stream
            # First try to use complete data, fall back to basic test data if not available
            test_data = None
            
            if stream or section:
                try:
                    from apps.results.services.heatmap_complete_data import get_complete_heatmap_data
                    # Try to detect stream from section name
                    detected_stream = stream
                    if not detected_stream and section:
                        # Detect stream from section name
                        if section.startswith(('PCMB', 'PCMC', 'PCME')):
                            detected_stream = 'Science'
                        elif section.startswith(('CEBA', 'CSBA', 'SEBA', 'PEBA', 'MSBA', 'MEBA')):
                            detected_stream = 'Commerce'
                    
                    if detected_stream:
                        print(f"[HEATMAP] Loading complete data for stream: {detected_stream}")
                        test_data = get_complete_heatmap_data(detected_stream)
                        print(f"[HEATMAP] ✓ Complete data loaded: {test_data.shape}")
                except Exception as e:
                    # Fall back to basic test data
                    print(f"[HEATMAP] ✗ Error loading complete data: {str(e)}")
                    test_data = None
            
            # Fallback to basic test data if complete data not available
            if test_data is None:
                print(f"[HEATMAP] Using fallback test data")
                if stream:
                    from apps.results.services.heatmap_phase2_data import get_all_heatmap_data
                    try:
                        test_data = get_all_heatmap_data(stream)
                    except ValueError:
                        return build_error_response(
                            APIError(f"Unknown stream: {stream}",
                                    code="INVALID_STREAM",
                                    status_code=status.HTTP_400_BAD_REQUEST)
                        )
                else:
                    # Fall back to Phase 1 test data for single section queries
                    test_data = get_heatmap_test_data()
            
            # Transform
            transformer = HeatmapTransformer(test_data)
            heatmap_records, errors = transformer.transform()
            
            # Filter by section if specified
            if section:
                heatmap_records = [r for r in heatmap_records if r['section'] == section]
            
            # Filter by stream if specified (already filtered by get_all_heatmap_data)
            if stream:
                heatmap_records = [r for r in heatmap_records if r['stream'].lower() == stream.lower()]
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Return grade distribution format (for dashboard heatmap)
            if format_type == 'grade-distribution' and section:
                # Reorganize data for heatmap: subjects as items with grade counts
                subjects_data = []
                for record in heatmap_records:
                    subjects_data.append({
                        'subject': record['subject'],
                        'distinction': record.get('distinction', 0),
                        'i class': record.get('i class', 0),
                        'ii class': record.get('ii class', 0),
                        'iii class': record.get('iii class', 0),
                        'centums': record.get('centums', 0),
                        'fail': record.get('fail', 0),
                    })
                
                return Response({
                    'status': 'success' if len(errors) == 0 else 'success_with_warnings',
                    'data': {
                        'section': section,
                        'subjects': subjects_data,
                        'total_subjects': len(subjects_data),
                    },
                    'filters': {
                        'section': section,
                        'stream': stream,
                    },
                    'errors': errors,
                    'response_time_ms': response_time_ms,
                }, status=status.HTTP_200_OK)
            
            # Return flat format (for compatibility)
            return Response({
                'status': 'success' if len(errors) == 0 else 'success_with_warnings',
                'data': heatmap_records,
                'count': len(heatmap_records),
                'filters': {
                    'section': section,
                    'stream': stream,
                },
                'errors': errors,
                'response_time_ms': response_time_ms,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Exception in HeatmapDataView GET: {str(e)}")
            import traceback
            traceback.print_exc()
            return build_error_response(
                APIError(f"Heatmap retrieval error: {str(e)}",
                        code="RETRIEVAL_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class HeatmapSampleView(APIView):
    """
    GET /api/heatmap/sample/
    
    Returns sample raw data and its heatmap transformation.
    Useful for frontend integration testing.
    """
    
    @track_performance
    def get(self, request):
        """Get sample data and transformation"""
        try:
            # Get sample raw data
            raw_df = get_heatmap_test_data()
            
            # Transform it
            transformer = HeatmapTransformer(raw_df)
            heatmap_records, errors = transformer.transform()
            
            return Response({
                'status': 'success',
                'sample': {
                    'input_format': {
                        'description': 'Row-based metrics with SECTION - SUBJECT columns',
                        'rows': list(raw_df.index),
                        'columns': list(raw_df.columns),
                        'shape': [len(raw_df.index), len(raw_df.columns)]
                    },
                    'raw_data': {
                        str(idx): {str(col): (float(raw_df.loc[idx, col]) if pd.notna(raw_df.loc[idx, col]) else None) 
                                            for col in raw_df.columns}
                        for idx in raw_df.index
                    },
                    'output_schema': {
                        'section': 'string (e.g. "PCMB A")',
                        'subject': 'string (e.g. "MATHS")',
                        'pass_percentage': 'float (0-100)',
                        'fail': 'integer',
                        'total': 'integer',
                        'stream': 'string ("Science" or "Commerce")',
                    },
                    'example': heatmap_records[0] if heatmap_records else None,
                },
                'transformed_data': heatmap_records,
                'statistics': {
                    'total_records': len(heatmap_records),
                    'errors': len(errors),
                },
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return build_error_response(
                APIError(f"Failed to generate sample data: {str(e)}",
                        code="SAMPLE_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
