import pandas as pd
import numpy as np
import re
from apps.results.services.config import (
    COLUMN_MAPPINGS,
    RESULT_CLASSIFICATION,
    RESERVED_COLUMNS,
    EXCLUDE_KEYWORDS,
    OTHER_IDENTIFIERS,
    NUMERIC_THRESHOLD,
)

def _normalize_col_name(name: str) -> str:
    """
    Normalize a column name for matching against reserved/exclude lists.
    Removes punctuation like '.', '/', '-', etc. and collapses whitespace.
    """
    s = str(name).lower().strip()
    s = re.sub(r"[^a-z0-9\\s]", " ", s)
    s = re.sub(r"\\s+", " ", s).strip()
    return s


def find_column(df, possible_names):
    """
    Find a column in DataFrame by checking possible variations
    
    Args:
        df: DataFrame with normalized columns
        possible_names: List of possible column names
        
    Returns:
        Column name if found, None otherwise
    """
    df_cols_lower = [col.lower().strip() for col in df.columns]
    
    for possible_name in possible_names:
        possible_name_lower = possible_name.lower().strip()
        if possible_name_lower in df_cols_lower:
            idx = df_cols_lower.index(possible_name_lower)
            return df.columns[idx]
    
    return None


def map_columns(df):
    """
    Auto-detect and map columns from various formats
    
    Args:
        df: Raw DataFrame
        
    Returns:
        DataFrame with standardized column names
        
    Raises:
        ValueError: If critical columns cannot be found
    """
    df = df.copy()
    
    # Normalize column names initially
    df.columns = df.columns.str.strip().str.lower()
    
    # Find critical columns
    reg_no_col = find_column(df, COLUMN_MAPPINGS["reg_no"])
    if not reg_no_col:
        raise ValueError("Cannot find registration number column. Checked: " + 
                        ", ".join(COLUMN_MAPPINGS["reg_no"]))
    
    grand_total_col = find_column(df, COLUMN_MAPPINGS["grand_total"])
    if not grand_total_col:
        raise ValueError("Cannot find grand total column. Checked: " + 
                        ", ".join(COLUMN_MAPPINGS["grand_total"]))
    
    # Map columns to standard names
    rename_map = {
        reg_no_col: "reg_no",
        grand_total_col: "grand_total",
    }
    
    # Optional columns
    percentage_col = find_column(df, COLUMN_MAPPINGS["percentage"])
    if percentage_col:
        rename_map[percentage_col] = "percentage"
    
    name_col = find_column(df, COLUMN_MAPPINGS["student_name"])
    if name_col:
        rename_map[name_col] = "student_name"
    
    df = df.rename(columns=rename_map)
    
    return df


def is_subject_column(df, col):
    """
    Determine if a column is a subject (numeric validation)
    
    Args:
        df: DataFrame
        col: Column name
        
    Returns:
        True if likely to be a subject, False otherwise
    """
    try:
        # Count numeric values in column
        numeric_values = pd.to_numeric(df[col], errors="coerce").notna().sum()
        total_values = len(df[col].dropna())
        
        if total_values == 0:
            return False
        
        numeric_ratio = numeric_values / total_values
        return numeric_ratio > NUMERIC_THRESHOLD
    except:
        return False


def detect_subjects(df):
    """
    Dynamically detect subject columns with better filtering
    
    Args:
        df: DataFrame with standardized columns
        
    Returns:
        List of subject column names
    """
    subject_cols = []
    
    reserved_normalized = {_normalize_col_name(c) for c in RESERVED_COLUMNS}
    exclude_keywords_normalized = [_normalize_col_name(k) for k in EXCLUDE_KEYWORDS]
    explicit_metadata_cols = {
        "k h s",
        "data completeness score",
        "was duplicate",
        "percentage was filled",
        "upload log",
        "data version",
        "processing version",
    }

    for col in df.columns:
        col_norm = _normalize_col_name(col)
        
        # Skip reserved columns
        if col_norm in reserved_normalized or col_norm in explicit_metadata_cols:
            continue
        
        # Skip if any exclude keyword is in column name
        if any(keyword in col_norm for keyword in exclude_keywords_normalized):
            continue
        
        # Validate it's actually numeric (not text metadata)
        if is_subject_column(df, col):
            subject_cols.append(col)
    
    return subject_cols


def clean_numeric(x):
    """Helper to clean numeric values"""
    try:
        if pd.isna(x):
            return np.nan
        return pd.to_numeric(
            str(x).replace("%", "").replace(",", "").strip(),
            errors="coerce"
        )
    except:
        return np.nan


def validate_section(df):
    """
    Validate and reconcile section information
    
    Args:
        df: DataFrame
        
    Returns:
        Tuple of (section_mismatches_count, quality_note)
    """
    mismatches = 0
    
    # Check if explicit section column exists
    if "sect" in df.columns and "section" not in df.columns:
        df["section"] = df["sect"]
    elif "sect" in df.columns and "section" in df.columns:
        # Both exist - validate
        df["sect_clean"] = df["sect"].astype(str).str.strip().str.upper()
        df["section_clean"] = df["section"].astype(str).str.strip().str.upper()
        
        mismatch_mask = df["sect_clean"] != df["section_clean"]
        mismatches = mismatch_mask.sum()
        
        # Use explicit column if provided, else use extracted
        df["section"] = df["sect"].fillna(df["section"])
        df = df.drop(["sect_clean", "section_clean", "sect"], axis=1, errors="ignore")
    else:
        # Extract from reg_no if section column doesn't exist
        if "section" not in df.columns:
            df["section"] = df["reg_no"].str[2:4].fillna("UNKNOWN")
    
    return mismatches


def validate_part_totals(df):
    """
    Validate that part totals sum correctly to grand total
    
    Args:
        df: DataFrame
        
    Returns:
        Count of mismatches found
    """
    mismatches = 0
    
    # Look for part total columns
    part1_col = find_column(df, [
        "part-1 total", "part1 total", "part 1 total",
        "part-1_total", "part1_total"
    ])
    part2_col = find_column(df, [
        "part-2 total", "part2 total", "part 2 total",
        "part-2_total", "part2_total"
    ])
    
    if part1_col and part2_col and "grand_total" in df.columns:
        # Clean columns
        df["part1_total_clean"] = df[part1_col].apply(clean_numeric)
        df["part2_total_clean"] = df[part2_col].apply(clean_numeric)
        
        # Calculate expected total
        df["calculated_total"] = df["part1_total_clean"] + df["part2_total_clean"]
        
        # Find mismatches
        valid_mask = (df["calculated_total"].notna()) & (df["grand_total"].notna())
        mismatch_mask = valid_mask & (abs(df["calculated_total"] - df["grand_total"]) > 0.5)
        mismatches = mismatch_mask.sum()
        
        # Clean up temp columns
        df = df.drop(["part1_total_clean", "part2_total_clean", "calculated_total"], 
                     axis=1, errors="ignore")
    
    return mismatches


def validate_percentage(df):
    """
    Validate percentage values against calculated percentage
    
    Args:
        df: DataFrame with grand_total and percentage columns
        
    Returns:
        Tuple of (mismatches_count, percentage_filled_count)
    """
    mismatches = 0
    filled_count = 0
    
    if "grand_total" not in df.columns:
        return 0, 0
    
    # Calculate expected percentage
    max_total = df["grand_total"].max()
    df["calculated_percentage"] = (df["grand_total"] / max_total * 100).round(2)
    
    if "percentage" in df.columns:
        df["percentage_clean"] = df["percentage"].apply(clean_numeric)

        # Excel often stores percentages as 0-1 floats (e.g., 0.8217 for 82.17%).
        # Detect that pattern and scale to 0-100 so classification works.
        try:
            pct_non_null = df["percentage_clean"].dropna()
            if len(pct_non_null) > 0:
                pct_max = float(pct_non_null.max())
                pct_median = float(pct_non_null.median())
                if 0 < pct_max <= 1.0 and 0 < pct_median <= 1.0:
                    df["percentage_clean"] = (df["percentage_clean"] * 100).round(2)
        except Exception:
            # If anything goes wrong, don't fail cleaning — just keep original values.
            pass
        
        # Find rows with provided percentage
        has_pct = df["percentage_clean"].notna()
        
        # Find mismatches (tolerance of 1%)
        valid_mask = has_pct & df["calculated_percentage"].notna()
        mismatch_mask = valid_mask & (abs(df["percentage_clean"] - df["calculated_percentage"]) > 1)
        mismatches = mismatch_mask.sum()
        
        # Fill missing percentages
        missing_mask = df["percentage_clean"].isna()
        filled_count = missing_mask.sum()
        df.loc[missing_mask, "percentage_clean"] = df.loc[missing_mask, "calculated_percentage"]
        
        df["percentage"] = df["percentage_clean"]
        df = df.drop(["percentage_clean", "calculated_percentage"], axis=1, errors="ignore")
    else:
        # Add calculated percentage
        filled_count = len(df)
        df["percentage"] = df["calculated_percentage"]
        df = df.drop(["calculated_percentage"], axis=1, errors="ignore")
    
    return mismatches, filled_count


def clean_data(df):
    """
    Clean and normalize student results data with PRODUCTION-GRADE defensive engineering
    
    Args:
        df: Raw DataFrame from Excel
        
    Returns:
        Tuple of (cleaned_df, quality_metrics)
        
    Raises:
        ValueError: If required columns are missing
    """
    df = df.copy()
    original_count = len(df)
    
    # Initialize comprehensive quality metrics
    quality_metrics = {
        "original_records": original_count,
        "invalid_reg_no_removed": 0,
        "duplicates_removed": 0,
        "missing_grand_total_removed": 0,
        "missing_percentage_filled": 0,
        "invalid_percentage_corrected": 0,
        "result_class_assigned": 0,
        "section_mismatches": 0,
        "total_mismatches": 0,
        "percentage_mismatches": 0,
        "alternate_identifiers_found": 0,
    }
    
    # Step 1: Map columns with auto-detection
    df = map_columns(df)
    
    # Step 1.5: WARN about alternate identifiers (SATS NO, ENROLLMENT NO)
    original_cols = df.columns
    for alt_id in OTHER_IDENTIFIERS:
        if alt_id in original_cols:
            quality_metrics["alternate_identifiers_found"] += 1
            # Don't use them - only use reg_no
    
    # Step 2: Clean registration numbers
    df["reg_no"] = (
        df["reg_no"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    
    # Remove invalid registrations
    invalid_mask = (df["reg_no"] == "NAN") | (df["reg_no"] == "") | (df["reg_no"].isna())
    quality_metrics["invalid_reg_no_removed"] = invalid_mask.sum()
    df = df[~invalid_mask]
    
    # Step 3: Clean grand_total
    df["grand_total"] = df["grand_total"].apply(clean_numeric)
    
    # Remove rows without grand_total (critical field)
    missing_gt_mask = df["grand_total"].isna()
    quality_metrics["missing_grand_total_removed"] = missing_gt_mask.sum()
    df = df[~missing_gt_mask]
    
    # Step 4: Validate SECTION (reconcile sect vs extracted)
    section_mismatches = validate_section(df)
    quality_metrics["section_mismatches"] = section_mismatches
    
    # Step 5: Validate PART TOTALS (if they exist)
    total_mismatches = validate_part_totals(df)
    quality_metrics["total_mismatches"] = total_mismatches
    
    # Step 6: Validate and fill PERCENTAGE
    pct_mismatches, pct_filled = validate_percentage(df)
    quality_metrics["percentage_mismatches"] = pct_mismatches
    quality_metrics["missing_percentage_filled"] = pct_filled
    
    # Ensure percentage exists (or create it)
    if "percentage" not in df.columns:
        max_total = df["grand_total"].max()
        df["percentage"] = (df["grand_total"] / max_total * 100).round(2)
        quality_metrics["missing_percentage_filled"] = len(df)
    
    # Step 7: Ensure percentage is numeric
    df["percentage"] = df["percentage"].apply(clean_numeric)
    
    # Step 8: Validate percentage range (0-100)
    invalid_pct_mask = (df["percentage"] < 0) | (df["percentage"] > 100)
    if invalid_pct_mask.any():
        quality_metrics["invalid_percentage_corrected"] = invalid_pct_mask.sum()
        max_total = df["grand_total"].max()
        df.loc[invalid_pct_mask, "percentage"] = (
            df.loc[invalid_pct_mask, "grand_total"] / max_total * 100
        )
    
    # Step 9: Data completeness scoring
    df["data_completeness_score"] = df.notna().sum(axis=1)
    
    # Step 10: Deduplication with smart logic
    before_dedup = len(df)
    df = df.sort_values(
        by=["reg_no", "grand_total", "data_completeness_score"],
        ascending=[True, False, False]
    )
    df = df.drop_duplicates(subset="reg_no", keep="first")
    quality_metrics["duplicates_removed"] = before_dedup - len(df)
    
    # Step 11: Auto-derive result class (DON'T trust input)
    df["result_class"] = df["percentage"].apply(classify_result)
    quality_metrics["result_class_assigned"] = len(df)
    
    # Step 12: Detect subjects dynamically (with better filtering)
    subject_cols = detect_subjects(df)
    
    # Step 13: Clean subject columns (make numeric)
    for col in subject_cols:
        if col not in df.columns:
            continue
        df[col] = df[col].apply(clean_numeric)
    
    # Step 14: Reset index
    df = df.reset_index(drop=True)
    
    # Final quality calculation
    quality_metrics["final_records"] = len(df)
    quality_metrics["records_removed_total"] = original_count - len(df)
    quality_metrics["retention_rate"] = round(
        (len(df) / original_count * 100) if original_count > 0 else 0, 2
    )
    
    # Determine if there are warnings
    has_warnings = (
        section_mismatches > 0 or
        total_mismatches > 0 or
        pct_mismatches > 0 or
        quality_metrics["alternate_identifiers_found"] > 0
    )
    quality_metrics["has_warnings"] = has_warnings
    
    return df, quality_metrics


def classify_result(percentage):
    """
    Classify result based on percentage (auto-derive, don't trust input)
    
    Args:
        percentage: Numeric percentage
        
    Returns:
        Result classification string
    """
    if pd.isna(percentage):
        return "INCOMPLETE"
    
    if percentage >= RESULT_CLASSIFICATION["DISTINCTION"]:
        return "DISTINCTION"
    elif percentage >= RESULT_CLASSIFICATION["FIRST_CLASS"]:
        return "FIRST_CLASS"
    elif percentage >= RESULT_CLASSIFICATION["SECOND_CLASS"]:
        return "SECOND_CLASS"
    elif percentage >= RESULT_CLASSIFICATION["PASS"]:
        return "PASS"
    else:
        return "FAIL"


def validate_cleaned_data(df, quality_metrics):
    """
    Validate cleaned data before saving
    
    Args:
        df: Cleaned DataFrame
        quality_metrics: Quality metrics dict
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df.empty:
        return False, "No valid records found after cleaning"
    
    if "reg_no" not in df.columns:
        return False, "reg_no column missing after cleaning"
    
    if "stream" not in df.columns:
        return False, "stream column missing"
    
    if df["reg_no"].isna().any():
        return False, "Some registration numbers are empty after cleaning"
    
    if quality_metrics["retention_rate"] < 10:
        return False, f"Retention rate too low ({quality_metrics['retention_rate']}%). Data might be invalid."
    
    return True, None
