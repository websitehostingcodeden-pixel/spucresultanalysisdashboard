"""
Analytics Engine for ARIS System

Transforms CLEAN student result data into accurate, presentation-ready analytics.

CORE PRINCIPLE: NEVER assume data is perfect — validate before analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from django.db.models import QuerySet, Q, Count, Avg
from apps.results.models import StudentResult


class AnalyticsValidationError(Exception):
    """Raised when analytics validation fails"""
    pass


class TopperDataCleaner:
    """
    Utility class for cleaning and standardizing topper data.
    
    Ensures:
    - Percentage is always numeric float (0-100)
    - Stream is normalized (SCIENCE/COMMERCE/None)
    - No null critical fields
    - Data is deduplicated
    """
    
    @staticmethod
    def clean_topper(row: Dict[str, Any], include_rank: bool = True) -> Dict[str, Any]:
        """
        Clean a single topper record.
        
        Args:
            row: DataFrame row or dict with topper data
            include_rank: Whether to include rank field
            
        Returns:
            Cleaned dictionary with standardized format
        """
        # Extract percentage and normalize
        percentage = TopperDataCleaner._normalize_percentage(row.get('percentage'))
        
        # Extract stream and normalize
        stream = TopperDataCleaner._normalize_stream(row.get('stream'))
        
        # Build cleaned dict
        cleaned = {
            "reg_no": str(row.get('reg_no', 'N/A')).strip(),
            "student_name": str(row.get('student_name', 'N/A')).strip() or 'N/A',
            "stream": stream,
            "section": str(row.get('section', 'N/A')).strip() or 'N/A',
            "marks": float(row.get('grand_total', 0)) if pd.notna(row.get('grand_total')) else 0.0,
            "percentage": percentage,
            "class_name": str(row.get('result_class', 'INCOMPLETE')).strip(),
        }
        
        # Add rank if provided
        if include_rank and 'rank' in row and pd.notna(row.get('rank')):
            cleaned['rank'] = int(row.get('rank', 0))
        
        # Add language (K/H/S) if available
        if pd.notna(row.get('language')) and row.get('language'):
            lang_value = str(row.get('language')).strip().upper()
            if lang_value in ['K', 'H', 'S']:
                language_map = {'K': 'Kannada', 'H': 'Hindi', 'S': 'Sanskrit'}
                cleaned['language'] = language_map.get(lang_value, lang_value)
        
        # Add subject marks if available
        if pd.notna(row.get('subject_marks_data')) and row.get('subject_marks_data'):
            cleaned['subject_marks'] = row.get('subject_marks_data')
        
        return cleaned
    
    @staticmethod
    def _normalize_percentage(value) -> float:
        """
        Convert percentage to float (0-100 range).
        
        Handles:
        - String percentages ("85%", "85.5%")
        - Decimals (0.85, 85.5)
        - Nulls (returns 0.0)
        """
        if value is None or pd.isna(value):
            return 0.0
        
        try:
            # Convert to string and remove % sign if present
            str_val = str(value).strip().rstrip('%')
            pct = float(str_val)
            
            # If in 0-1 range, convert to 0-100
            if pct <= 1.0:
                pct = pct * 100
            
            # Clamp to 0-100 range
            pct = max(0.0, min(100.0, pct))
            
            return round(pct, 2)
        except (ValueError, TypeError):
            print(f"Warning: Invalid percentage: {value}, defaulting to 0.0")
            return 0.0
    
    @staticmethod
    def _normalize_stream(value) -> str or None:
        """
        Normalize stream value to standard format.
        
        Valid: SCIENCE, COMMERCE, None
        """
        if not value or pd.isna(value):
            return None
        
        normalized = str(value).upper().strip()
        if normalized in ['SCIENCE', 'COMMERCE']:
            return normalized
        
        print(f"Warning: Invalid stream: {value}, defaulting to None")
        return None


class StrictAnalyticsEngine:
    """
    Production-grade analytics engine with mandatory validation.
    
    RULES:
    1. No duplicate reg_no allowed
    2. All counts must be reproducible
    3. Consistency checks mandatory before returning
    4. Fail fast on any validation error
    """
    
    def __init__(self, queryset: QuerySet = None):
        """
        Initialize analytics engine with cleaned data.
        
        Args:
            queryset: Django QuerySet of StudentResult objects
                     If None, uses all StudentResult objects
        """
        if queryset is None:
            queryset = StudentResult.objects.all()
        
        self.queryset = queryset
        self.df = None
        self.results = {
            "status": "pending",
            "summary": {},
            "toppers": {},
            "sections": [],
            "subjects": {},
            "insights": {}
        }
    
    # ==================== STEP 1: VALIDATION ====================
    
    def _validate_dataset(self) -> bool:
        """
        Validate dataset integrity before processing.
        
        Checks:
        - Dataset not empty
        - No duplicate reg_no
        - All required fields present
        - Percentage values are numeric
        - Result class values are valid
        
        Raises:
            AnalyticsValidationError: If validation fails
        """
        if self.df is None or len(self.df) == 0:
            raise AnalyticsValidationError("Dataset is empty")
        
        # Check for duplicate reg_no
        duplicates = self.df['reg_no'].duplicated().sum()
        if duplicates > 0:
            raise AnalyticsValidationError(
                f"Found {duplicates} duplicate reg_no values. "
                "Use cleaned data from PART 1."
            )
        
        # Check required fields
        required_fields = ['reg_no', 'section', 'percentage', 'result_class']
        missing_fields = [f for f in required_fields if f not in self.df.columns]
        if missing_fields:
            raise AnalyticsValidationError(
                f"Missing required fields: {missing_fields}"
            )
        
        # Validate percentage numeric
        if not pd.api.types.is_numeric_dtype(self.df['percentage']):
            raise AnalyticsValidationError(
                "Percentage column must be numeric"
            )
        
        # Validate percentage range
        invalid_percentages = (
            (self.df['percentage'] < 0) | (self.df['percentage'] > 100)
        ).sum()
        if invalid_percentages > 0:
            raise AnalyticsValidationError(
                f"Found {invalid_percentages} percentages outside 0-100 range"
            )
        
        # Validate result_class values
        valid_classes = {
            'DISTINCTION', 'FIRST_CLASS', 'SECOND_CLASS', 
            'PASS', 'FAIL', 'INCOMPLETE'
        }
        invalid_classes = ~self.df['result_class'].isin(valid_classes)
        if invalid_classes.sum() > 0:
            raise AnalyticsValidationError(
                f"Found {invalid_classes.sum()} invalid result_class values"
            )
        
        print("OK: Dataset validation passed")
        return True
    
    # ==================== STEP 2: GLOBAL SUMMARY ====================
    
    def _compute_global_summary(self) -> Dict[str, Any]:
        """
        Compute global statistics for entire institution.
        
        Returns:
            Dictionary with:
            - total_students
            - total_passed
            - total_failed
            - pass_percentage
            - average_percentage
            - distinction_count
            - first_class_count
            - second_class_count
            - pass_class_count
        """
        total_students = len(self.df)
        
        # Count by result class
        result_counts = self.df['result_class'].value_counts().to_dict()
        
        total_passed = len(
            self.df[self.df['result_class'] != 'FAIL']
        )
        total_failed = result_counts.get('FAIL', 0)
        
        # Verify counts sum correctly
        if total_passed + total_failed != total_students:
            raise AnalyticsValidationError(
                f"Count mismatch: passed({total_passed}) + "
                f"failed({total_failed}) != total({total_students})"
            )
        
        pass_percentage = (total_passed / total_students * 100) if total_students > 0 else 0
        average_percentage = float(self.df['percentage'].mean())
        
        summary = {
            "total_students": int(total_students),
            "total_passed": int(total_passed),
            "total_failed": int(total_failed),
            "pass_percentage": round(pass_percentage, 2),
            "average_percentage": round(average_percentage, 2),
            "distinction_count": int(result_counts.get('DISTINCTION', 0)),
            "first_class_count": int(result_counts.get('FIRST_CLASS', 0)),
            "second_class_count": int(result_counts.get('SECOND_CLASS', 0)),
            "pass_class_count": int(result_counts.get('PASS', 0))
        }
        
        print("OK: Global summary computed")
        return summary
    
    # ==================== STEP 3: TOPPERS (STRICT) ====================
    
    def _compute_toppers(self) -> Dict[str, List[Dict]]:
        """
        Generate college, stream, and section toppers with strict ranking.
        Includes student name, all marks, and grades.
        
        RULES:
        - Sort by percentage DESC
        - Handle ties by sorting by reg_no
        - No duplicate students
        - Top 10 per category
        - Use standardized, cleaned data format
        
        Returns:
            Dictionary with college, science, commerce toppers
            (all cleaned and standardized)
        """
        toppers = {}
        
        # College Toppers (Top 10 overall)
        df_sorted = self.df.sort_values(
            by=['percentage', 'reg_no'],
            ascending=[False, True]
        ).head(10)
        
        college_toppers = []
        for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
            cleaned = TopperDataCleaner.clean_topper(row, include_rank=True)
            cleaned['rank'] = rank  # Set correct rank
            college_toppers.append(cleaned)
        
        toppers['college'] = college_toppers
        
        # Science Toppers (if stream column exists)
        if 'stream' in self.df.columns:
            df_science = self.df[
                self.df['stream'] == 'SCIENCE'
            ].sort_values(
                by=['percentage', 'reg_no'],
                ascending=[False, True]
            ).head(10)
            
            science_toppers = []
            for rank, (_, row) in enumerate(df_science.iterrows(), 1):
                cleaned = TopperDataCleaner.clean_topper(row, include_rank=True)
                cleaned['rank'] = rank
                science_toppers.append(cleaned)
            
            toppers['science'] = science_toppers
            
            # Commerce Toppers
            df_commerce = self.df[
                self.df['stream'] == 'COMMERCE'
            ].sort_values(
                by=['percentage', 'reg_no'],
                ascending=[False, True]
            ).head(10)
            
            commerce_toppers = []
            for rank, (_, row) in enumerate(df_commerce.iterrows(), 1):
                cleaned = TopperDataCleaner.clean_topper(row, include_rank=True)
                cleaned['rank'] = rank
                commerce_toppers.append(cleaned)
            
            toppers['commerce'] = commerce_toppers
        else:
            # If no stream column, set empty lists
            toppers['science'] = []
            toppers['commerce'] = []
        
        print("OK: Toppers computed (college + stream)")
        return toppers
    
    # ==================== STEP 4: SECTION-WISE TOPPERS ====================
    
    def _compute_section_toppers(self) -> Dict[str, List[Dict]]:
        """
        Compute top 10 students per section.
        
        Section toppers use the SAME cleaned format as other toppers,
        except they do NOT include rank (rank is per-section and not displayed).
        
        Returns:
            Dictionary with section_X: [toppers] format
        """
        section_toppers = {}
        
        for section in sorted(self.df['section'].unique()):
            df_section = self.df[
                self.df['section'] == section
            ].sort_values(
                by=['percentage', 'reg_no'],
                ascending=[False, True]
            ).head(10)
            
            toppers_in_section = []
            for _, row in df_section.iterrows():
                cleaned = TopperDataCleaner.clean_topper(row, include_rank=False)
                cleaned.pop("rank", None)
                toppers_in_section.append(cleaned)
            
            if toppers_in_section:  # Only if section has students
                section_toppers[f"section_{section}"] = toppers_in_section
        
        print(f"OK: Section-wise toppers computed for {len(section_toppers)} sections")
        return section_toppers
    
    # ==================== STEP 5: SECTION PERFORMANCE ====================
    
    def _compute_section_performance(self) -> List[Dict]:
        """
        Compute performance metrics for each section.
        
        Returns:
            List of sections with metrics:
            - appeared, passed, failed, distinction, first_class, 
              second_class, pass_class, pass_percentage
        """
        section_performance = []
        total_from_sections = 0
        
        for section in sorted(self.df['section'].unique()):
            df_section = self.df[self.df['section'] == section]
            
            appeared = len(df_section)
            passed = len(df_section[df_section['result_class'] != 'FAIL'])
            failed = len(df_section[df_section['result_class'] == 'FAIL'])
            
            # Verify counts sum
            if passed + failed != appeared:
                raise AnalyticsValidationError(
                    f"Section {section}: passed({passed}) + "
                    f"failed({failed}) != appeared({appeared})"
                )
            
            # Count by class
            result_counts = df_section['result_class'].value_counts().to_dict()
            distinction = result_counts.get('DISTINCTION', 0)
            first_class = result_counts.get('FIRST_CLASS', 0)
            second_class = result_counts.get('SECOND_CLASS', 0)
            pass_class = result_counts.get('PASS', 0)
            
            # Verify individual counts sum to passed
            if distinction + first_class + second_class + pass_class != passed:
                raise AnalyticsValidationError(
                    f"Section {section}: class counts don't sum to passed"
                )
            
            pass_percentage = (passed / appeared * 100) if appeared > 0 else 0
            average_percentage = float(df_section['percentage'].mean())
            
            section_performance.append({
                "section": section,
                "appeared": int(appeared),
                "passed": int(passed),
                "failed": int(failed),
                "distinction": int(distinction),
                "first_class": int(first_class),
                "second_class": int(second_class),
                "pass_class": int(pass_class),
                "pass_percentage": round(pass_percentage, 2),
                "average_percentage": round(average_percentage, 2)
            })
            
            total_from_sections += appeared
        
        # Verify total students match
        if total_from_sections != len(self.df):
            raise AnalyticsValidationError(
                f"Section totals ({total_from_sections}) != "
                f"total students ({len(self.df)})"
            )
        
        print(f"OK: Section performance computed ({len(section_performance)} sections)")
        return section_performance
    
    # ==================== STEP 6: SUBJECT-WISE ANALYSIS ====================
    
    def _get_subject_columns(self) -> List[str]:
        """Identify subject columns (numeric, not metadata)"""
        metadata_cols = {
            'id', 'reg_no', 'student_name', 'section', 'semester',
            'grand_total', 'percentage', 'result_class', 'stream',
            'data_completeness_score', 'was_duplicate', 
            'percentage_was_filled', 'upload_log_id', 'created_at', 'updated_at'
        }
        
        subjects = []
        for col in self.df.columns:
            if col not in metadata_cols and pd.api.types.is_numeric_dtype(self.df[col]):
                subjects.append(col)
        
        return subjects
    
    def _compute_subject_analysis(self) -> Dict[str, Any]:
        """
        Compute subject-wise statistics and grade distribution.
        
        Grade buckets (mutually exclusive):
        >95, 90-94.9, 85-89.9, 80-84.9, 75-79.9, 70-74.9, 65-69.9,
        60-64.9, 55-59.9, 50-54.9, 45-49.9, 40-44.9, 35-39.9, <35
        
        Returns:
            Dictionary with subject stats and distributions
        """
        subjects = self._get_subject_columns()
        
        if not subjects:
            print("Info: No subject columns found, skipping subject analysis")
            return {}
        
        subject_analysis = {}
        
        for subject in subjects:
            # Get non-null values
            subject_data = self.df[subject].dropna()
            
            if len(subject_data) == 0:
                continue
            
            average_marks = float(subject_data.mean())
            
            # Define grade buckets (mutually exclusive)
            bins = [0, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
            labels = [
                '<35', '35-39.9', '40-44.9', '45-49.9', '50-54.9',
                '55-59.9', '60-64.9', '65-69.9', '70-74.9', '75-79.9',
                '80-84.9', '85-89.9', '90-94.9', '>95'
            ]
            
            # Categorize marks
            grades = pd.cut(subject_data, bins=bins, labels=labels, right=False)
            distribution = grades.value_counts().sort_index().to_dict()
            
            # Convert to int counts
            distribution_int = {k: int(v) for k, v in distribution.items()}
            
            # Verify total matches non-null count
            if sum(distribution_int.values()) != len(subject_data):
                raise AnalyticsValidationError(
                    f"Subject {subject}: distribution counts don't match non-null count"
                )
            
            subject_analysis[subject] = {
                "average_marks": round(average_marks, 2),
                "total_students": int(len(subject_data)),
                "null_count": int(self.df[subject].isna().sum()),
                "distribution": distribution_int
            }
        
        print(f"OK: Subject analysis computed ({len(subject_analysis)} subjects)")
        return subject_analysis
    
    # ==================== STEP 7: CONSISTENCY CHECKS ====================
    
    def _validate_consistency(self) -> bool:
        """
        Mandatory consistency checks before returning results.
        
        Checks:
        - total_students == sum(section appeared)
        - passed + failed == total_students
        - No negative values
        - All percentages in 0-100
        - Rankings sorted correctly
        
        Raises:
            AnalyticsValidationError: If any check fails
        """
        summary = self.results['summary']
        sections = self.results['sections']
        
        # Check 1: Student count match
        section_total = sum(s['appeared'] for s in sections)
        if section_total != summary['total_students']:
            raise AnalyticsValidationError(
                f"Consistency check failed: "
                f"section totals ({section_total}) != "
                f"global total ({summary['total_students']})"
            )
        
        # Check 2: Pass + Fail = Total
        if summary['total_passed'] + summary['total_failed'] != summary['total_students']:
            raise AnalyticsValidationError(
                f"Consistency check failed: "
                f"passed({summary['total_passed']}) + "
                f"failed({summary['total_failed']}) != "
                f"total({summary['total_students']})"
            )
        
        # Check 3: No negative values
        for key, value in summary.items():
            if isinstance(value, (int, float)) and value < 0:
                raise AnalyticsValidationError(
                    f"Consistency check failed: negative value in {key}={value}"
                )
        
        # Check 4: Percentages in valid range
        if not (0 <= summary['pass_percentage'] <= 100):
            raise AnalyticsValidationError(
                f"Pass percentage {summary['pass_percentage']} outside valid range"
            )
        
        if not (0 <= summary['average_percentage'] <= 100):
            raise AnalyticsValidationError(
                f"Average percentage {summary['average_percentage']} outside valid range"
            )
        
        # Check 5: Rankings are sorted
        for rank_list in self.results['toppers'].values():
            if isinstance(rank_list, list) and len(rank_list) > 1:
                percentages = [r['percentage'] for r in rank_list]
                if percentages != sorted(percentages, reverse=True):
                    raise AnalyticsValidationError(
                        "Rankings not sorted correctly by percentage DESC"
                    )
        
        print("OK: All consistency checks passed")
        return True
    
    # ==================== STEP 8: DATA INSIGHTS ====================
    
    def _generate_insights(self) -> Dict[str, Any]:
        """
        Generate auto-flagged insights for easy interpretation.
        
        Flags:
        - highest_section (max pass %)
        - lowest_section (min pass %)
        - top_student
        - weak_subject
        - strong_subject
        """
        insights = {}
        
        # Highest section by pass percentage
        if self.results['sections']:
            section_by_pass = sorted(
                self.results['sections'],
                key=lambda x: x['pass_percentage'],
                reverse=True
            )
            insights['highest_section'] = {
                "name": section_by_pass[0]['section'],
                "pass_percentage": section_by_pass[0]['pass_percentage']
            }
            insights['lowest_section'] = {
                "name": section_by_pass[-1]['section'],
                "pass_percentage": section_by_pass[-1]['pass_percentage']
            }
        
        # Top student
        if self.results['toppers'].get('college'):
            top = self.results['toppers']['college'][0]
            insights['top_student'] = {
                "reg_no": top['reg_no'],
                "student_name": top['student_name'],
                "percentage": top['percentage']
            }
        
        # Subject analysis insights
        if self.results['subjects']:
            subject_avgs = {
                k: v['average_marks'] 
                for k, v in self.results['subjects'].items()
            }
            if subject_avgs:
                insights['strong_subject'] = {
                    "name": max(subject_avgs, key=subject_avgs.get),
                    "average": subject_avgs[max(subject_avgs, key=subject_avgs.get)]
                }
                insights['weak_subject'] = {
                    "name": min(subject_avgs, key=subject_avgs.get),
                    "average": subject_avgs[min(subject_avgs, key=subject_avgs.get)]
                }
        
        print("OK: Data insights generated")
        return insights
    
    # ==================== MAIN EXECUTION ====================
    
    def generate(self) -> Dict[str, Any]:
        """
        Execute complete analytics pipeline with full validation.
        
        Returns:
            Structured analytics JSON or error response
        """
        try:
            # Convert queryset to DataFrame
            print("\nStarting Analytics Pipeline...")
            print("-" * 50)
            
            self.df = pd.DataFrame.from_records(
                self.queryset.values(),
                index='reg_no'
            ).reset_index()
            
            # STEP 1: Validate
            self._validate_dataset()
            
            # STEP 2: Global Summary
            self.results['summary'] = self._compute_global_summary()
            
            # STEP 3: Toppers (College + Stream)
            self.results['toppers'] = self._compute_toppers()
            
            # STEP 4: Section-wise Toppers
            section_toppers = self._compute_section_toppers()
            self.results['toppers'].update(section_toppers)  # Merge into toppers dict
            
            # STEP 5: Section Performance
            self.results['sections'] = self._compute_section_performance()
            
            # STEP 6: Subject Analysis
            self.results['subjects'] = self._compute_subject_analysis()
            
            # STEP 7: Consistency Checks
            self._validate_consistency()
            
            # STEP 8: Insights
            self.results['insights'] = self._generate_insights()
            
            # Mark success
            self.results['status'] = 'success'
            
            print("-" * 50)
            print("OK: Analytics pipeline completed successfully")
            
            return self.results
            
        except AnalyticsValidationError as e:
            print(f"ERROR: Analytics validation failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "failed_step": "validation"
            }
        
        except Exception as e:
            print(f"ERROR: Unexpected error in analytics: {str(e)}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "failed_step": "unknown"
            }


def compute_analytics(queryset: QuerySet = None) -> Dict[str, Any]:
    """
    Convenience function to generate analytics from queryset.
    
    Args:
        queryset: Django QuerySet of StudentResult objects
        
    Returns:
        Complete analytics dictionary
    """
    engine = StrictAnalyticsEngine(queryset)
    return engine.generate()
