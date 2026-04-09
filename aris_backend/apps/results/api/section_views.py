"""
Section Data Transformation API Views

Provides endpoints for transforming row-based Excel metrics into section-wise JSON objects.

Endpoints:
- POST /api/sections/transform/: Upload raw Excel data and transform to sections
- GET /api/sections/sample/: Get sample test data and transformed output
"""

import time
import json
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.results.services.section_transformer import SectionTransformer, validate_section_data
from apps.results.services.test_data import get_raw_dataframe
from apps.results.api.serializers import SectionDataResponseSerializer, SectionDataSerializer
from apps.results.api.api_utils import build_error_response, APIError, track_performance


class SectionTransformView(APIView):
    """
    POST /api/sections/transform/
    
    Transform row-based Excel metrics into section-wise JSON objects.
    
    Expected input: JSON with metrics as rows
    {
        "Enrolled": {"PCMB A": 52, "PCMB B": 48, ...},
        "Absent": {"PCMB A": 0, "PCMB B": 2, ...},
        ...
    }
    
    Or upload Excel file with metrics in rows and sections in columns.
    """
    
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    @track_performance
    def post(self, request):
        """Transform section metrics"""
        try:
            start_time = time.time()
            
            # Check if JSON data or file upload
            if request.FILES:
                # Excel file upload
                file = request.FILES.get('file')
                if not file:
                    return build_error_response(
                        APIError("No file uploaded", code="MISSING_FILE",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
                
                try:
                    excel_data = pd.read_excel(file)
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
                    excel_data = pd.DataFrame(json_data)
                else:
                    return build_error_response(
                        APIError("Request data must be a JSON object",
                                code="INVALID_FORMAT",
                                status_code=status.HTTP_400_BAD_REQUEST)
                    )
            
            # Transform
            transformer = SectionTransformer.from_dataframe(excel_data)
            sections, errors = transformer.transform()
            
            # Validate
            is_valid, validation_errors = validate_section_data(sections)
            
            # Serialize
            serializer = SectionDataResponseSerializer({
                'status': 'success' if is_valid else 'error',
                'data': sections,
                'count': len(sections),
                'errors': errors + validation_errors,
                'validation_summary': {
                    'total_sections': 12,
                    'sections_found': len(sections),
                    'validation_passed': is_valid,
                    'error_count': len(errors) + len(validation_errors),
                }
            })
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return Response({
                'status': 'success' if is_valid else 'success_with_warnings',
                'data': serializer.data['data'],
                'count': serializer.data['count'],
                'errors': serializer.data['errors'],
                'validation_summary': serializer.data['validation_summary'],
                'response_time_ms': response_time_ms,
            }, status=status.HTTP_200_OK if is_valid else status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Exception in SectionTransformView: {str(e)}")
            import traceback
            traceback.print_exc()
            return build_error_response(
                APIError(f"Section transformation error: {str(e)}",
                        code="TRANSFORM_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


class SectionSampleDataView(APIView):
    """
    GET /api/sections/sample/
    
    Returns sample raw Excel data and its transformed output.
    Useful for understanding the transformation format.
    """
    
    @track_performance
    def get(self, request):
        """Get sample data and transformation"""
        try:
            # Get sample raw data
            raw_df = get_raw_dataframe()
            
            # Transform it
            transformer = SectionTransformer.from_dataframe(raw_df)
            sections, errors = transformer.transform()
            
            # Validate
            is_valid, validation_errors = validate_section_data(sections)
            
            return Response({
                'status': 'success',
                'sample': {
                    'input_format': {
                        'description': 'Row-based Excel metrics',
                        'rows': list(raw_df.index),
                        'columns': list(raw_df.columns),
                        'shape': [len(raw_df.index), len(raw_df.columns)]
                    },
                    'raw_data': {
                        str(idx): {str(col): raw_df.loc[idx, col] for col in raw_df.columns}
                        for idx in raw_df.index
                    },
                    'output_format': {
                        'description': 'Transformed section objects',
                        'schema': {
                            'section': 'string',
                            'stream': 'Science|Commerce',
                            'enrolled': 'integer',
                            'absent': 'integer',
                            'appeared': 'integer',
                            'distinction': 'integer',
                            'first_class': 'integer',
                            'second_class': 'integer',
                            'pass_class': 'integer',
                            'detained': 'integer',
                            'promoted': 'integer',
                            'pass_percentage': 'float (0-100)'
                        },
                        'example': sections[0] if sections else None,
                    },
                    'statistics': {
                        'total_sections': len(sections),
                        'science_sections': len([s for s in sections if s['stream'] == 'Science']),
                        'commerce_sections': len([s for s in sections if s['stream'] == 'Commerce']),
                        'validation_passed': is_valid,
                    }
                },
                'transformed_data': sections,
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return build_error_response(
                APIError(f"Failed to generate sample data: {str(e)}",
                        code="SAMPLE_ERROR",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
