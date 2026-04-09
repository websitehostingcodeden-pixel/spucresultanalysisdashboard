"""
Data Contract & Schema Enforcement

Defines the strict contract between PART 1 (Data Cleaning) and PART 2 (Analytics).
If data doesn't satisfy this contract → Part 2 refuses to run.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
from enum import Enum


class DataContractError(Exception):
    """Raised when data violates the contract"""
    pass


class StreamType(str, Enum):
    """Valid stream values"""
    SCIENCE = "SCIENCE"
    COMMERCE = "COMMERCE"


class ResultClass(str, Enum):
    """Valid result classifications"""
    DISTINCTION = "DISTINCTION"
    FIRST_CLASS = "FIRST_CLASS"
    SECOND_CLASS = "SECOND_CLASS"
    PASS = "PASS"
    FAIL = "FAIL"
    INCOMPLETE = "INCOMPLETE"


class DataContract:
    """
    Enforces the strict data contract between PART 1 and PART 2.
    
    SCHEMA:
    {
        "reg_no": "string (unique, non-null)",
        "student_name": "string (optional)",
        "stream": "SCIENCE | COMMERCE",
        "section": "string (non-null)",
        "percentage": "float (0-100, non-null)",
        "result_class": "DISTINCTION|FIRST_CLASS|SECOND_CLASS|PASS|FAIL|INCOMPLETE",
        "grand_total": "float (optional)",
        "data_completeness_score": "int (0-100)",
    }
    
    CONTRACT RULES (MANDATORY):
    1. No duplicate reg_no
    2. All required fields present
    3. Percentage in range 0-100
    4. Stream is SCIENCE or COMMERCE
    5. Result class is valid
    6. Section is non-null
    7. Data completeness score is int
    """
    
    # Required fields
    REQUIRED_FIELDS = {
        'reg_no': str,
        'stream': str,
        'section': str,
        'percentage': (float, int),
        'result_class': str,
    }
    
    # Optional fields
    OPTIONAL_FIELDS = {
        'student_name': str,
        'grand_total': (float, int),
        'data_completeness_score': int,
    }
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame against contract.
        
        Returns:
            (is_valid: bool, errors: List[str])
            
        Raises:
            DataContractError if critical violations found
        """
        errors = []
        
        # Check 1: Not empty
        if df is None or len(df) == 0:
            raise DataContractError("Dataset is empty")
        
        # Check 2: Required fields present
        missing_fields = set(DataContract.REQUIRED_FIELDS.keys()) - set(df.columns)
        if missing_fields:
            raise DataContractError(
                f"Missing required fields: {missing_fields}"
            )
        
        # Check 3: No NULL/NaN reg_no
        null_reg_nos = df['reg_no'].isna().sum()
        if null_reg_nos > 0:
            raise DataContractError(
                f"Contract violation: {null_reg_nos} null reg_no values found. "
                "reg_no is required and must be present. PART 1 must provide reg_no."
            )
        
        # Check 4: No duplicates on reg_no
        duplicates = df['reg_no'].duplicated().sum()
        if duplicates > 0:
            raise DataContractError(
                f"Contract violation: {duplicates} duplicate reg_no values found. "
                "PART 1 must ensure unique reg_no."
            )
        
        # Check 5: Percentage not null
        null_pct = df['percentage'].isna().sum()
        if null_pct > 0:
            raise DataContractError(
                f"Contract violation: {null_pct} null percentage values found. "
                "Percentage is required. PART 1 must calculate percentage."
            )
        
        # Check 6: Percentage range
        invalid_pct = (
            (df['percentage'] < 0) | (df['percentage'] > 100)
        ).sum()
        if invalid_pct > 0:
            raise DataContractError(
                f"Contract violation: {invalid_pct} percentages outside 0-100 range. "
                "PART 1 must validate percentages."
            )
        
        # Check 5: Stream validity
        valid_streams = {StreamType.SCIENCE.value, StreamType.COMMERCE.value}
        invalid_streams = ~df['stream'].isin(valid_streams)
        if invalid_streams.sum() > 0:
            raise DataContractError(
                f"Contract violation: {invalid_streams.sum()} invalid stream values. "
                f"Must be {valid_streams}. PART 1 must normalize stream values."
            )
        
        # Check 6: Result class validity
        valid_classes = {rc.value for rc in ResultClass}
        invalid_classes = ~df['result_class'].isin(valid_classes)
        if invalid_classes.sum() > 0:
            raise DataContractError(
                f"Contract violation: {invalid_classes.sum()} invalid result_class values. "
                f"Must be one of {valid_classes}. PART 1 must derive result_class."
            )
        
        # Check 7: Section non-null
        null_sections = df['section'].isna().sum()
        if null_sections > 0:
            raise DataContractError(
                f"Contract violation: {null_sections} null section values. "
                "Section is required. PART 1 must provide section."
            )
        
        # Check 8: Data completeness score if present
        if 'data_completeness_score' in df.columns:
            invalid_completeness = (
                (df['data_completeness_score'] < 0) | 
                (df['data_completeness_score'] > 100)
            ).sum()
            if invalid_completeness > 0:
                errors.append(
                    f"Warning: {invalid_completeness} data_completeness_score values "
                    "outside 0-100 range"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_record(record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single record against contract.
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        # Check required fields
        for field, field_type in DataContract.REQUIRED_FIELDS.items():
            if field not in record:
                return False, f"Missing required field: {field}"
            
            if record[field] is None:
                return False, f"Required field {field} is null"
        
        # Check reg_no is string
        if not isinstance(record['reg_no'], str):
            return False, f"reg_no must be string, got {type(record['reg_no'])}"
        
        # Check stream validity
        if record['stream'] not in {s.value for s in StreamType}:
            return False, f"Invalid stream: {record['stream']}"
        
        # Check percentage range
        if not (0 <= record['percentage'] <= 100):
            return False, f"Percentage {record['percentage']} outside 0-100"
        
        # Check result_class validity
        if record['result_class'] not in {rc.value for rc in ResultClass}:
            return False, f"Invalid result_class: {record['result_class']}"
        
        # Check section non-null
        if not record.get('section'):
            return False, "Section is required"
        
        return True, ""
    
    @staticmethod
    def get_contract_schema() -> Dict[str, Any]:
        """
        Return the contract schema as documentation.
        """
        return {
            "contract_version": "1.0",
            "required_fields": {
                name: typ.__name__ if hasattr(typ, '__name__') else str(typ)
                for name, typ in DataContract.REQUIRED_FIELDS.items()
            },
            "optional_fields": {
                name: typ.__name__ if hasattr(typ, '__name__') else str(typ)
                for name, typ in DataContract.OPTIONAL_FIELDS.items()
            },
            "valid_streams": [s.value for s in StreamType],
            "valid_result_classes": [rc.value for rc in ResultClass],
            "constraints": {
                "percentage": "0 ≤ percentage ≤ 100",
                "reg_no": "unique, non-null",
                "section": "non-null",
                "stream": "required, one of SCIENCE/COMMERCE"
            }
        }
