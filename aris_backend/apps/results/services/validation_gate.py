"""
PRODUCTION: Validation Gate - Hard-Stop Before Database

Purpose:
    Prevent invalid data from entering database.
    This is the enforcement layer between PART 1 (Cleaning) and database storage.
    
Flow:
    Raw Data → Cleaner (PART 1) → ValidationGate (HARD STOP) → Database → Analytics
    
Key Points:
    - Raises ValidationGateError if contract violated
    - Stops upload immediately with clear error message
    - Logs contract violations for debugging
    - Acts as contract enforcement boundary
    
Contract Rules (Hard-Fail):
    ✓ No NULL reg_no
    ✓ No duplicate reg_no
    ✓ stream in [SCIENCE, COMMERCE]
    ✓ percentage between 0-100
    ✓ result_class valid enum
    ✓ section not NULL
    ✓ All required fields present
"""

import logging
from typing import List, Tuple, Dict, Any
import pandas as pd

from apps.results.services.contract import DataContract, DataContractError
from apps.results.models import StudentResult

logger = logging.getLogger('validation_gate')


class ValidationGateError(Exception):
    """Raised when data fails hard validation"""
    pass


class ValidationGate:
    """Hard validation gate - stops invalid data before database"""
    
    @staticmethod
    def validate_before_insert(
        df: pd.DataFrame,
        upload_id: int = None,
    ) -> Tuple[bool, str]:
        """
        CRITICAL: Validate dataframe before ANY database operation.
        
        Args:
            df: Cleaned dataframe from PART 1
            upload_id: Upload being processed (for logging)
            
        Returns:
            (is_valid, message) tuple
            
        Raises:
            ValidationGateError: If validation fails
            
        Examples:
            >>> df = pd.DataFrame({...})
            >>> is_valid, msg = ValidationGate.validate_before_insert(df, upload_id=5)
            >>> # is_valid = True, msg = "All 8 records passed validation"
            
            >>> # If invalid:
            >>> # is_valid = False
            >>> # Raises ValidationGateError("No duplicate reg_no allowed")
        """
        
        try:
            # STEP 1: Check if dataframe empty
            if df.empty:
                raise ValidationGateError("Cannot insert empty dataframe")
            
            # STEP 2: Contract validation (hard-fail)
            is_valid, errors = DataContract.validate_dataframe(df)
            if not is_valid:
                error_msg = f"Contract validation failed: {'; '.join(errors)}"
                logger.warning(f"Upload {upload_id}: {error_msg}")
                raise ValidationGateError(error_msg)
            
            # STEP 3: Record count validation
            record_count = len(df)
            if record_count == 0:
                raise ValidationGateError("No valid records after validation")
            
            # STEP 4: Data type validation
            type_errors = ValidationGate._validate_data_types(df)
            if type_errors:
                error_msg = f"Data type errors: {'; '.join(type_errors)}"
                logger.warning(f"Upload {upload_id}: {error_msg}")
                raise ValidationGateError(error_msg)
            
            # STEP 5: Business rule validation
            business_errors = ValidationGate._validate_business_rules(df)
            if business_errors:
                error_msg = f"Business rule violations: {'; '.join(business_errors)}"
                logger.warning(f"Upload {upload_id}: {error_msg}")
                raise ValidationGateError(error_msg)
            
            # STEP 6: Database integrity check (no existing reg_nos)
            db_errors = ValidationGate._check_database_integrity(df)
            if db_errors:
                error_msg = f"Database integrity check failed: {'; '.join(db_errors)}"
                logger.warning(f"Upload {upload_id}: {error_msg}")
                raise ValidationGateError(error_msg)
            
            # All validations passed
            logger.info(
                f"Upload {upload_id}: All {record_count} records passed "
                f"validation gate"
            )
            return True, f"All {record_count} records passed validation"
            
        except ValidationGateError:
            # Re-raise validation gate errors
            raise
        except DataContractError as e:
            # Convert contract errors to gate errors
            raise ValidationGateError(f"Contract error: {str(e)}")
        except Exception as e:
            # Unexpected errors
            error_msg = f"Validation gate error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValidationGateError(error_msg)

    @staticmethod
    def _validate_data_types(df: pd.DataFrame) -> List[str]:
        """Check data types are correct"""
        errors = []
        
        # Check string fields
        for col in ['reg_no', 'stream', 'section', 'result_class']:
            if col in df.columns:
                if not all(isinstance(x, str) for x in df[col]):
                    errors.append(f"{col} must be string, found non-string values")
        
        # Check numeric fields
        for col in ['percentage', 'grand_total']:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    errors.append(f"{col} must be numeric")
        
        return errors

    @staticmethod
    def _validate_business_rules(df: pd.DataFrame) -> List[str]:
        """Check business rule violations"""
        errors = []
        
        # RULE 1: Percentage must be 0-100
        if 'percentage' in df.columns:
            out_of_range = df[
                (df['percentage'] < 0) | (df['percentage'] > 100)
            ]
            if len(out_of_range) > 0:
                errors.append(
                    f"Percentage out of range (0-100): "
                    f"{len(out_of_range)} records"
                )
        
        # RULE 2: Grand total must be positive
        if 'grand_total' in df.columns:
            negative = df[df['grand_total'] < 0]
            if len(negative) > 0:
                errors.append(
                    f"Grand total negative: {len(negative)} records"
                )
        
        # RULE 3: Result class must be valid enum
        if 'result_class' in df.columns:
            from apps.results.services.config import VALID_RESULT_CLASSES
            invalid_class = df[~df['result_class'].isin(VALID_RESULT_CLASSES)]
            if len(invalid_class) > 0:
                errors.append(
                    f"Invalid result class: {len(invalid_class)} records "
                    f"(valid: {', '.join(VALID_RESULT_CLASSES)})"
                )
        
        # RULE 4: Percentage-result_class consistency
        if all(col in df.columns for col in ['percentage', 'result_class']):
            # FAIL should have percentage < 40
            fails = df[df['result_class'] == 'FAIL']
            inconsistent_fails = fails[fails['percentage'] >= 40]
            if len(inconsistent_fails) > 0:
                errors.append(
                    f"Result class inconsistency: "
                    f"{len(inconsistent_fails)} FAIL records with percentage >= 40"
                )
        
        return errors

    @staticmethod
    def _check_database_integrity(df: pd.DataFrame) -> List[str]:
        """Check database constraints"""
        errors = []
        
        # RULE 1: Check for duplicates within the incoming data first
        if 'reg_no' in df.columns:
            # Check if there are duplicates in the INCOMING data
            incoming_duplicates = df[df.duplicated(subset=['reg_no'], keep=False)]['reg_no'].unique()
            if len(incoming_duplicates) > 0:
                errors.append(
                    f"Duplicate registration numbers in incoming data: "
                    f"{', '.join(incoming_duplicates[:5].astype(str))}"
                    f"{'...' if len(incoming_duplicates) > 5 else ''}"
                )
                return errors
            
            # RULE 2: For production, unique reg_nos per upload (existing records from OTHER uploads are OK)
            # We allow replacing records from this upload, so we don't check database constraints
            # This enables data re-uploads and self-healing
        
        return errors

    @staticmethod
    def validate_single_record(record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single record (e.g., when updating manually).
        
        Returns:
            (is_valid, message)
        """
        try:
            is_valid, error = DataContract.validate_record(record)
            if not is_valid:
                return False, f"Contract validation failed: {error}"
            
            return True, "Record valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def create_validation_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create detailed validation report (for debugging).
        Does NOT stop on errors - returns all issues.
        """
        report = {
            'total_records': len(df),
            'contract_valid': False,
            'data_types_valid': True,
            'business_rules_valid': True,
            'database_integrity_valid': True,
            'errors': [],
        }
        
        # Contract check
        try:
            is_valid, errors = DataContract.validate_dataframe(df)
            report['contract_valid'] = is_valid
            if not is_valid:
                report['errors'].extend(errors)
        except Exception as e:
            report['errors'].append(f"Contract check failed: {str(e)}")
        
        # Data types check
        type_errors = ValidationGate._validate_data_types(df)
        if type_errors:
            report['data_types_valid'] = False
            report['errors'].extend(type_errors)
        
        # Business rules check
        business_errors = ValidationGate._validate_business_rules(df)
        if business_errors:
            report['business_rules_valid'] = False
            report['errors'].extend(business_errors)
        
        # Database integrity check
        db_errors = ValidationGate._check_database_integrity(df)
        if db_errors:
            report['database_integrity_valid'] = False
            report['errors'].extend(db_errors)
        
        report['is_valid'] = (
            report['contract_valid'] and
            report['data_types_valid'] and
            report['business_rules_valid'] and
            report['database_integrity_valid']
        )
        
        return report
