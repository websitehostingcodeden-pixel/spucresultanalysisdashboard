from apps.results.models import StudentResult, UploadLog
from apps.results.services.excel_reader import read_excel
from apps.results.services.cleaner import clean_data, validate_cleaned_data, detect_subjects
from apps.results.services.validation_gate import ValidationGate, ValidationGateError
from apps.results.services.deduplicator import (
    deduplicate_upload,
    cleanup_database_duplicates,
    report_deduplication
)
import pandas as pd


def process_upload(file, upload_log=None):
    """
    Main service to process uploaded Excel file with quality tracking
    
    Pipeline:
        1. Read Excel
        2. Clean data (PART 1)
        3. Validate cleaned data
        4. VALIDATION GATE (hard-stop before database) ← CRITICAL
        5. Save to database
        6. Generate snapshot
        7. Update upload log
    
    Args:
        file: Django UploadedFile object
        upload_log: UploadLog instance (optional) for tracking
        
    Returns:
        Tuple of (success, records_created, quality_metrics, error_message)
    """
    try:
        # Read Excel file
        raw_df = read_excel(file)
        
        # Clean data (returns DataFrame and quality metrics)
        clean_df, quality_metrics = clean_data(raw_df)
        
        # STEP 2A: Deduplicate incoming data (CRITICAL - force removal)
        clean_df, upload_dedup_stats = deduplicate_upload(clean_df)
        if upload_dedup_stats["records_removed"] > 0:
            quality_metrics["upload_duplicates_removed"] = upload_dedup_stats["records_removed"]
        
        # VERIFY: Double-check no duplicates remain in critical columns
        if 'reg_no' in clean_df.columns:
            remaining_dupes = clean_df[clean_df.duplicated(subset=['reg_no'], keep=False)]
            if len(remaining_dupes) > 0:
                error_msg = f"CRITICAL: Deduplicator failed! Still have {len(remaining_dupes)} duplicate records"
                if upload_log:
                    upload_log.status = "FAILED"
                    upload_log.error_message = error_msg
                    upload_log.save()
                return False, 0, quality_metrics, error_msg
        
        # Validate cleaned data
        is_valid, error = validate_cleaned_data(clean_df, quality_metrics)
        if not is_valid:
            if upload_log:
                upload_log.status = "FAILED"
                upload_log.error_message = error
                upload_log.save()
            return False, 0, quality_metrics, error
        
        # STEP 2B: Cleanup existing database duplicates before validation
        db_dedup_stats = cleanup_database_duplicates(upload_log)
        if db_dedup_stats["records_deleted"] > 0:
            quality_metrics["db_duplicates_removed"] = db_dedup_stats["records_deleted"]
        
        # CRITICAL: Validation Gate - Hard-stop before database
        upload_id = upload_log.id if upload_log else None
        try:
            is_valid, validation_msg = ValidationGate.validate_before_insert(
                clean_df,
                upload_id=upload_id,
            )
            if not is_valid:
                if upload_log:
                    upload_log.status = "FAILED"
                    upload_log.error_message = validation_msg
                    upload_log.save()
                return False, 0, quality_metrics, validation_msg
        except ValidationGateError as e:
            # Contract violation - hard-fail
            error_msg = str(e)
            if upload_log:
                upload_log.status = "FAILED"
                upload_log.error_message = error_msg
                upload_log.save()
            return False, 0, quality_metrics, error_msg
        
        # Subject columns: use same dynamic detection as clean_data (avoids missing e.g. Kannada,
        # Mathematics, or other names that don't match a fixed keyword list).
        subject_cols = detect_subjects(clean_df)
        numeric_cols = [
            col for col in subject_cols
            if col in clean_df.columns and pd.api.types.is_numeric_dtype(clean_df[col])
        ]
        
        # Bulk create or update records
        records_created = 0
        for _, row in clean_df.iterrows():
            # Extract subject marks using pre-calculated numeric columns
            subject_marks = {}
            for col in numeric_cols:
                value = row.get(col)
                if pd.notna(value):
                    # Clean column name for display
                    subject_name = col.replace('marks_', '').replace('_', ' ').upper()
                    subject_marks[subject_name] = float(value)

            # Derive 2nd-language marks when sheets provide K/H/S code but not an explicit marks column.
            #
            # Supported formats:
            # - If PART-1 TOTAL exists: 2nd language = PART-1 TOTAL - ENGLISH
            # - Else, if GRAND TOTAL exists: 2nd language = GRAND TOTAL - sum(other detected subject marks)
            def _first_present(keys):
                for k in keys:
                    if k in row.index:
                        return k
                return None

            english_col = _first_present(["english"])
            part1_total_col = _first_present([
                "part-1 total", "part1 total", "part 1 total",
                "part-1_total", "part1_total"
            ])
            lang_code_col = _first_present(["k/h/s", "language"])

            def _derive_second_language_name():
                name = "SECOND LANGUAGE"
                if lang_code_col and pd.notna(row.get(lang_code_col)):
                    code = str(row.get(lang_code_col)).strip().upper()
                    name = {"K": "KANNADA", "H": "HINDI", "S": "SANSKRIT"}.get(code, name)
                return name

            derived_second_lang = None

            # Path A: PART-1 TOTAL - ENGLISH
            if english_col and part1_total_col:
                eng_val = pd.to_numeric(row.get(english_col), errors="coerce")
                p1_val = pd.to_numeric(row.get(part1_total_col), errors="coerce")
                if pd.notna(eng_val) and pd.notna(p1_val):
                    derived_second_lang = float(p1_val - eng_val)

            # Path B (fallback): GRAND TOTAL - sum(detected subject marks)
            if derived_second_lang is None:
                gt_val = pd.to_numeric(row.get("grand_total"), errors="coerce") if "grand_total" in row.index else pd.NA
                if pd.notna(gt_val) and subject_marks:
                    derived_second_lang = float(gt_val - sum(subject_marks.values()))

            if derived_second_lang is not None:
                # Basic sanity: avoid negative/zero artifacts from bad totals.
                if derived_second_lang > 0:
                    lang_name = _derive_second_language_name()
                    # Don't overwrite if the sheet already has an explicit language marks column.
                    subject_marks.setdefault(lang_name, round(derived_second_lang, 2))
            
            # Extract language choice (K/H/S). Some sheets use column name "K/H/S".
            language_val = None
            raw_lang = None
            if 'language' in row and pd.notna(row.get('language')):
                raw_lang = row.get('language')
            elif 'k/h/s' in row and pd.notna(row.get('k/h/s')):
                raw_lang = row.get('k/h/s')

            if raw_lang is not None:
                lang = str(raw_lang).strip().upper()
                if lang in ['K', 'H', 'S']:
                    language_val = lang
            
            obj, created = StudentResult.objects.update_or_create(
                reg_no=row["reg_no"],
                defaults={
                    "student_name": row.get("student_name"),
                    "stream": row.get("stream", "UNKNOWN"),
                    "section": row.get("section", "UNKNOWN"),
                    "percentage": row.get("percentage"),
                    "grand_total": row.get("grand_total"),
                    "result_class": row.get("result_class", "INCOMPLETE"),
                    "subject_marks_data": subject_marks,
                    "language": language_val,
                    "data_completeness_score": row.get("data_completeness_score", 0),
                    "percentage_was_filled": quality_metrics["missing_percentage_filled"] > 0,
                    "data_version": "v1.0",  # PRODUCTION: Set versioning
                    "processing_version": "cleaner_v1",  # PRODUCTION: Track cleaner version
                    "upload_log": upload_log,  # Link to upload
                }
            )
            if created:
                records_created += 1
        
        # Update upload log with metrics
        if upload_log:
            # Determine status
            if quality_metrics.get("has_warnings", False):
                status_value = "SUCCESS_WITH_WARNINGS"
            else:
                status_value = "SUCCESS"
            
            upload_log.status = status_value
            upload_log.records_processed = quality_metrics["original_records"]
            upload_log.records_kept = len(clean_df)
            
            # Data integrity metrics (includes deduplication stats)
            upload_log.invalid_reg_no_removed = quality_metrics["invalid_reg_no_removed"]
            upload_log.duplicates_removed = quality_metrics.get("upload_duplicates_removed", 0)
            
            # Add database cleanup info to status message
            if db_dedup_stats["records_deleted"] > 0:
                upload_log.status_message = (
                    f"Upload: {upload_dedup_stats['records_removed']} duplicates removed; "
                    f"Database: {db_dedup_stats['records_deleted']} duplicates cleaned"
                )
            upload_log.missing_grand_total_removed = quality_metrics["missing_grand_total_removed"]
            upload_log.missing_percentage_filled = quality_metrics["missing_percentage_filled"]
            upload_log.invalid_percentage_corrected = quality_metrics["invalid_percentage_corrected"]
            
            # Data validation metrics (NEW)
            upload_log.section_mismatches = quality_metrics.get("section_mismatches", 0)
            upload_log.total_mismatches = quality_metrics.get("total_mismatches", 0)
            upload_log.percentage_mismatches = quality_metrics.get("percentage_mismatches", 0)
            upload_log.alternate_identifiers_found = quality_metrics.get("alternate_identifiers_found", 0)
            
            # Quality score
            upload_log.retention_rate = quality_metrics["retention_rate"]
            
            # PRODUCTION: Set versioning
            upload_log.data_version = "v1.0"
            upload_log.processing_version = "cleaner_v1"
            
            upload_log.save()
        
        # PRODUCTION: Generate analytics snapshot for this upload
        # This caches the analytics so API can return <100ms response
        try:
            from apps.results.services.snapshot import SnapshotManager
            from apps.results.services.snapshot import SnapshotManager
            
            # Invalidate global/stream/section caches (new data available)
            SnapshotManager.invalidate_all_caches()
            
            # Generate snapshot for this specific upload
            if upload_log:
                snapshot_result = SnapshotManager.compute_and_cache_upload_analytics(
                    upload_log.id
                )
                if not snapshot_result.get('success'):
                    # Log snapshot error but don't fail upload
                    import logging
                    logger = logging.getLogger('analytics')
                    logger.warning(
                        f"Failed to generate snapshot for upload {upload_log.id}: "
                        f"{snapshot_result.get('error')}"
                    )
        except Exception as e:
            # Snapshot generation error - log but don't fail
            import logging
            logger = logging.getLogger('snapshots')
            logger.warning(f"Snapshot generation error: {str(e)}")
        
        return True, records_created, quality_metrics, None
        
    except Exception as e:
        error_msg = str(e)
        if upload_log:
            upload_log.status = "FAILED"
            upload_log.error_message = error_msg
            upload_log.save()
        return False, 0, {}, error_msg
