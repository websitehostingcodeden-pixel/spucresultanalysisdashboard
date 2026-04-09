"""
DATA DEDUPLICATOR

Removes duplicate records from:
1. Incoming upload data (keeps highest score record)
2. Existing database records (before validation)

This ensures clean data and prevents "duplicate registration" validation errors.
"""

import pandas as pd
from apps.results.models import StudentResult


def deduplicate_upload(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Remove duplicates from incoming Excel data.
    
    Strategy: For each duplicate registration number, keep the record with:
    1. Highest total marks (if available)
    2. Most recent row (if marks are equal)
    3. Most complete data (if same marks)
    
    Args:
        df: Raw DataFrame from Excel
        
    Returns:
        (deduplicated_df, dedup_stats)
    """
    if not isinstance(df, pd.DataFrame) or len(df) == 0:
        return df, {"duplicates_found": 0, "records_removed": 0}
    
    # Track original count
    original_count = len(df)
    
    # Only deduplicate if reg_no column exists
    if 'reg_no' not in df.columns:
        return df, {"duplicates_found": 0, "records_removed": 0}
    
    # Find duplicates
    duplicate_reg_nos = df[df.duplicated(subset=['reg_no'], keep=False)]['reg_no'].unique()
    duplicates_found = len(duplicate_reg_nos)
    
    if duplicates_found == 0:
        return df, {"duplicates_found": 0, "records_removed": 0}
    
    # Keep best record per registration
    # Priority: highest grand_total, then highest percentage, then first occurrence
    if 'grand_total' in df.columns:
        # Sort by grand_total descending (highest first), then keep first occurrence
        df_dedup = df.sort_values(['reg_no', 'grand_total'], 
                                   ascending=[True, False])
        df_dedup = df_dedup.drop_duplicates(subset=['reg_no'], keep='first')
    elif 'percentage' in df.columns:
        # Sort by percentage descending, then keep first
        df_dedup = df.sort_values(['reg_no', 'percentage'], 
                                   ascending=[True, False])
        df_dedup = df_dedup.drop_duplicates(subset=['reg_no'], keep='first')
    else:
        # Just keep first occurrence
        df_dedup = df.drop_duplicates(subset=['reg_no'], keep='first')
    
    # Reset index
    df_dedup = df_dedup.reset_index(drop=True)
    
    records_removed = original_count - len(df_dedup)
    
    return df_dedup, {
        "duplicates_found": duplicates_found,
        "records_removed": records_removed,
        "duplicate_reg_nos": duplicate_reg_nos.tolist()[:10]  # First 10 for reporting
    }


def cleanup_database_duplicates(upload_log=None) -> dict:
    """
    Remove duplicate records from database for a given upload.
    
    For each registration number, keeps the record with highest grand_total.
    
    Args:
        upload_log: UploadLog instance (if provided, cleans only that upload's records)
        
    Returns:
        stats dict with records_deleted, duplicates_found info
    """
    stats = {
        "duplicates_found": 0,
        "records_deleted": 0,
        "affected_reg_nos": []
    }
    
    # Get all or filtered records
    if upload_log:
        queryset = StudentResult.objects.filter(upload_log=upload_log)
    else:
        queryset = StudentResult.objects.all()
    
    if not queryset.exists():
        return stats
    
    # Find duplicate registration numbers
    from django.db.models import Count, Max
    duplicates = queryset.values('reg_no').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if not duplicates.exists():
        return stats
    
    for dup in duplicates:
        reg_no = dup['reg_no']
        
        # Get all records for this registration
        records = queryset.filter(reg_no=reg_no).order_by('-grand_total', '-id')
        
        if records.exists():
            # Keep the first (highest grand_total), delete others
            keep_record = records.first()
            to_delete = records.exclude(id=keep_record.id)
            
            deleted_count = to_delete.count()
            to_delete.delete()
            
            stats["duplicates_found"] += 1
            stats["records_deleted"] += deleted_count
            stats["affected_reg_nos"].append(reg_no)
    
    return stats


def report_deduplication(upload_stats: dict, db_stats: dict) -> str:
    """
    Generate user-friendly report about deduplication.
    
    Args:
        upload_stats: Stats from deduplicate_upload()
        db_stats: Stats from cleanup_database_duplicates()
        
    Returns:
        Formatted report string
    """
    report_lines = []
    
    # Upload deduplication
    if upload_stats["records_removed"] > 0:
        report_lines.append(
            f"✓ Cleaned upload data: Removed {upload_stats['records_removed']} "
            f"duplicate records (kept {upload_stats['duplicates_found']} unique registrations)"
        )
        if upload_stats["duplicate_reg_nos"]:
            report_lines.append(
                f"  Affected registrations: {', '.join(upload_stats['duplicate_reg_nos'][:5])}"
                f"{'...' if len(upload_stats['duplicate_reg_nos']) > 5 else ''}"
            )
    
    # Database cleanup
    if db_stats["records_deleted"] > 0:
        report_lines.append(
            f"✓ Cleaned database: Removed {db_stats['records_deleted']} "
            f"duplicate records ({db_stats['duplicates_found']} registrations)"
        )
    
    if not report_lines:
        report_lines.append("✓ No duplicates found - data is clean")
    
    return "\n".join(report_lines)
