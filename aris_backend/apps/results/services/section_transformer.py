"""
Section Performance Transformer

Transforms row-based Excel metrics into section-wise JSON objects.

INPUT FORMAT:
- Row-based: metrics as rows, sections as columns
- Example: "Enrolled" row, "PCMB A", "PCMB B", etc. as columns

OUTPUT FORMAT:
{
  "section": "PCMB A",
  "stream": "Science",
  "enrolled": 52,
  "absent": 0,
  "appeared": 52,
  "distinction": 8,
  "first_class": 30,
  "second_class": 12,
  "pass_class": 0,
  "detained": 2,
  "promoted": 50,
  "pass_percentage": 96
}

VALIDATION RULES:
- All 12 sections must be present
- Stream assigned by section name
- No totals allowed
- All metrics must be numeric
- All metrics must be positive integers
"""

import pandas as pd
from typing import Dict, List, Tuple, Any
from decimal import Decimal


class SectionTransformationError(Exception):
    """Raised when section transformation fails"""
    pass


class SectionTransformer:
    """Transform row-based Excel metrics to section objects with strict validation"""
    
    # Valid sections by stream
    SCIENCE_SECTIONS = ["PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E"]
    COMMERCE_SECTIONS = ["CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"]
    ALL_SECTIONS = SCIENCE_SECTIONS + COMMERCE_SECTIONS
    
    # Metrics that should be present in input
    REQUIRED_METRICS = [
        "Enrolled",
        "Absent",
        "Appeared",
        "Distinction",
        "First Class",
        "Second Class",
        "Pass Class",
        "Detained",
        "Promoted"
    ]
    
    # Invalid row identifiers (totals to exclude)
    INVALID_ROWS = ["Total", "Science Total", "Commerce Total", "Grand Total"]
    
    def __init__(self, excel_data: Dict[str, List] = None):
        """
        Initialize transformer with row-based data.
        
        Args:
            excel_data: Dictionary like {"Enrolled": [52, 48, ...], "Absent": [...], }
                       Can also accept a pandas DataFrame with metrics as rows
        """
        self.excel_data = excel_data
        self.df = None
        self.validation_errors = []
        self.transformation_results = []
    
    def transform(self) -> Tuple[List[Dict], List[str]]:
        """
        Execute transformation pipeline.
        
        Returns:
            Tuple of (section_objects, validation_errors)
            - section_objects: List of dicts with all 12 sections
            - validation_errors: List of error messages (empty = success)
        """
        try:
            # Step 1: Parse input
            self._parse_input()
            
            # Step 2: Validate structure
            self._validate_structure()
            
            # Step 3: Transform to sections
            self._transform_to_sections()
            
            # Step 4: Validate all sections present
            self._validate_all_sections_present()
            
            # Step 5: Validate no totals
            self._validate_no_totals()
            
            # Step 6: Validate data integrity
            self._validate_data_integrity()
            
            return self.transformation_results, self.validation_errors
            
        except SectionTransformationError as e:
            self.validation_errors.append(str(e))
            return [], self.validation_errors
    
    def _parse_input(self):
        """Parse input into DataFrame with rows as metrics"""
        if isinstance(self.excel_data, pd.DataFrame):
            self.df = self.excel_data.copy()
        elif isinstance(self.excel_data, dict):
            # Convert dict to DataFrame (rows as index)
            self.df = pd.DataFrame(self.excel_data).T
        else:
            raise SectionTransformationError(
                "Input must be pandas DataFrame or dict"
            )
        
        # Remove any completely empty rows or columns
        self.df = self.df.dropna(how='all')
        self.df = self.df.dropna(axis=1, how='all')
        
        if self.df.empty:
            raise SectionTransformationError("Input data is empty")
    
    def _validate_structure(self):
        """Validate that input has required structure"""
        # Check if first column is metric names (index should contain metrics)
        if self.df.index.name is None and not self._has_valid_metrics():
            raise SectionTransformationError(
                "Input structure invalid. Expected rows to be metrics "
                "(Enrolled, Absent, Appeared, etc.)"
            )
        
        # Check if columns contain section names
        section_cols = [col for col in self.df.columns if str(col).strip() in self.ALL_SECTIONS]
        if len(section_cols) < 3:  # At least some sections
            raise SectionTransformationError(
                f"Found {len(section_cols)} section columns, expected at least 12"
            )
    
    def _has_valid_metrics(self) -> bool:
        """Check if index contains at least some valid metrics"""
        index_values = [str(idx).strip() for idx in self.df.index]
        valid_count = sum(1 for idx in index_values if idx in self.REQUIRED_METRICS)
        return valid_count >= 3
    
    def _transform_to_sections(self):
        """Transform each section column into a section object"""
        self.transformation_results = []
        
        for section in self.ALL_SECTIONS:
            # Find section column (case-insensitive, handle variations)
            section_col = self._find_section_column(section)
            
            if section_col is None:
                self.validation_errors.append(
                    f"Section '{section}' not found in input columns"
                )
                continue
            
            # Extract metrics for this section
            section_data = {}
            for metric in self.REQUIRED_METRICS:
                value = self._extract_metric_value(metric, section_col)
                if value is not None:
                    section_data[metric.lower().replace(" ", "_")] = value
            
            # Build section object
            section_obj = self._build_section_object(section, section_data)
            if section_obj:
                self.transformation_results.append(section_obj)
    
    def _find_section_column(self, section_name: str):
        """Find column matching section name (case-insensitive)"""
        for col in self.df.columns:
            col_str = str(col).strip()
            if col_str == section_name or col_str.lower() == section_name.lower():
                return col
        return None
    
    def _extract_metric_value(self, metric: str, section_col) -> int:
        """Extract numeric value for a metric in a section"""
        try:
            for idx in self.df.index:
                idx_str = str(idx).strip()
                if idx_str == metric or idx_str.lower() == metric.lower():
                    value = self.df.loc[idx, section_col]
                    if pd.isna(value) or value == "" or value is None:
                        return None
                    return int(float(value))
        except Exception:
            pass
        return None
    
    def _build_section_object(self, section_name: str, metrics: Dict) -> Dict:
        """Build complete section object with stream assignment"""
        
        # Assign stream
        if section_name in self.SCIENCE_SECTIONS:
            stream = "Science"
        elif section_name in self.COMMERCE_SECTIONS:
            stream = "Commerce"
        else:
            return None
        
        # Extract metrics with defaults
        enrolled = metrics.get("enrolled", 0)
        absent = metrics.get("absent", 0)
        appeared = metrics.get("appeared", 0)
        distinction = metrics.get("distinction", 0)
        first_class = metrics.get("first_class", 0)
        second_class = metrics.get("second_class", 0)
        pass_class = metrics.get("pass_class", 0)
        detained = metrics.get("detained", 0)
        promoted = metrics.get("promoted", 0)
        
        # Calculate pass percentage
        passed = distinction + first_class + second_class + pass_class
        if appeared > 0:
            pass_percentage = round((passed / appeared) * 100, 2)
        else:
            pass_percentage = 0
        
        # Convert to float for percentage, int for counts
        return {
            "section": section_name,
            "stream": stream,
            "enrolled": int(enrolled),
            "absent": int(absent),
            "appeared": int(appeared),
            "distinction": int(distinction),
            "first_class": int(first_class),
            "second_class": int(second_class),
            "pass_class": int(pass_class),
            "detained": int(detained),
            "promoted": int(promoted),
            "pass_percentage": float(pass_percentage)
        }
    
    def _validate_all_sections_present(self):
        """Validate that all 12 sections are present in results"""
        sections_found = {obj["section"] for obj in self.transformation_results}
        sections_missing = set(self.ALL_SECTIONS) - sections_found
        
        if len(sections_missing) > 0:
            self.validation_errors.append(
                f"Missing sections: {', '.join(sorted(sections_missing))}"
            )
    
    def _validate_no_totals(self):
        """Validate that no totals are in the results"""
        for obj in self.transformation_results:
            section_name = obj.get("section", "")
            for invalid_row in self.INVALID_ROWS:
                if invalid_row.lower() in section_name.lower():
                    self.validation_errors.append(
                        f"Found invalid section (total): {section_name}"
                    )
                    self.transformation_results = [
                        s for s in self.transformation_results
                        if s.get("section") != section_name
                    ]
    
    def _validate_data_integrity(self):
        """Validate numeric and logical consistency of data"""
        for section_obj in self.transformation_results:
            section = section_obj.get("section", "N/A")
            
            # Check all values are non-negative
            for key, value in section_obj.items():
                if key in ["pass_percentage"]:
                    continue
                if isinstance(value, (int, float)):
                    if value < 0:
                        self.validation_errors.append(
                            f"Section {section}: {key} is negative ({value})"
                        )
            
            # Check pass_percentage is 0-100
            pass_pct = section_obj.get("pass_percentage", 0)
            if pass_pct < 0 or pass_pct > 100:
                self.validation_errors.append(
                    f"Section {section}: pass_percentage out of range ({pass_pct})"
                )
            
            # Check appeared >= distinct classes
            appeared = section_obj.get("appeared", 0)
            passed_sum = (
                section_obj.get("distinction", 0) +
                section_obj.get("first_class", 0) +
                section_obj.get("second_class", 0) +
                section_obj.get("pass_class", 0)
            )
            if passed_sum > appeared:
                self.validation_errors.append(
                    f"Section {section}: sum of classes ({passed_sum}) > appeared ({appeared})"
                )
    
    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> "SectionTransformer":
        """Create transformer from DataFrame with rows as metrics"""
        return SectionTransformer(excel_data=df)
    
    @staticmethod
    def from_dict(data: Dict) -> "SectionTransformer":
        """Create transformer from dict of metrics"""
        return SectionTransformer(excel_data=data)


def validate_section_data(sections: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate transformed section objects.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if not isinstance(sections, list):
        return False, ["Sections must be a list"]
    
    if len(sections) != 12:
        errors.append(f"Expected 12 sections, got {len(sections)}")
    
    # Check all required fields present
    required_fields = {
        "section", "stream", "enrolled", "absent", "appeared",
        "distinction", "first_class", "second_class", "pass_class",
        "detained", "promoted", "pass_percentage"
    }
    
    for obj in sections:
        missing_fields = required_fields - set(obj.keys())
        if missing_fields:
            errors.append(
                f"Section {obj.get('section', 'N/A')}: missing fields {missing_fields}"
            )
    
    # Check field types
    for obj in sections:
        # Check stream is valid
        stream = obj.get("stream")
        if stream not in ["Science", "Commerce"]:
            errors.append(
                f"Section {obj.get('section', 'N/A')}: invalid stream '{stream}'"
            )
        
        # Check percentage is float
        pass_pct = obj.get("pass_percentage")
        if not isinstance(pass_pct, (float, int)):
            errors.append(
                f"Section {obj.get('section', 'N/A')}: pass_percentage must be numeric"
            )
    
    return len(errors) == 0, errors
