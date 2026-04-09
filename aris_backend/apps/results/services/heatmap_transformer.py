"""
Heatmap Data Transformer

Transforms section-subject level result data into visualization-ready heatmap records.

INPUT FORMAT (Row-based):
Metric,PCMB A - MATHS,PCMB A - ENG,PCMB B - MATHS,PCMB B - ENG,...
Distinction,22,20,19,18,...
First Class,19,18,17,16,...
Second Class,6,8,8,7,...
Pass Class,5,6,5,6,...
Total,52,52,46,47,...

OUTPUT FORMAT (Flat):
[
  {
    "section": "PCMB A",
    "subject": "MATHS",
    "pass_percentage": 96.15,
    "fail": 0,
    "total": 52,
    "stream": "Science"
  },
  ...
]

PASS % CALCULATION:
pass_percentage = ((Distinction + First Class + Second Class + Pass Class) / Total) * 100
FAIL is NOT included in pass count
"""

import pandas as pd
from typing import Dict, List, Tuple, Any
from decimal import Decimal


class HeatmapTransformationError(Exception):
    """Raised when heatmap transformation fails"""
    pass


class HeatmapTransformer:
    """Transform row-based section-subject metrics to flat heatmap records"""
    
    # Valid sections by stream
    SCIENCE_SECTIONS = ["PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E"]
    COMMERCE_SECTIONS = ["CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"]
    ALL_SECTIONS = SCIENCE_SECTIONS + COMMERCE_SECTIONS
    
    # Stream mapping
    STREAM_MAP = {
        "SCIENCE": "Science",
        "COMMERCE": "Commerce",
    }
    
    # Metrics that define pass/fail
    PASS_METRICS = ["Distinction", "First Class", "Second Class", "Pass Class"]
    FAIL_METRIC = "Fail"
    TOTAL_METRIC = "Total"
    
    def __init__(self, excel_data: Dict[str, Dict] = None):
        """
        Initialize transformer with row-based data.
        
        Args:
            excel_data: Dictionary like:
            {
              "Distinction": {"PCMB A - MATHS": 22, "PCMB A - ENG": 20, ...},
              "First Class": {"PCMB A - MATHS": 19, ...},
              ...
            }
        """
        self.excel_data = excel_data
        self.df = None
        self.validation_errors = []
        self.transformation_results = []
        self.section_subject_mapping = {}  # Track unique sections and subjects
    
    def transform(self) -> Tuple[List[Dict], List[str]]:
        """
        Execute transformation pipeline.
        
        Returns:
            Tuple of (heatmap_records, validation_errors)
        """
        try:
            # Step 1: Parse input
            self._parse_input()
            
            # Step 2: Extract section-subject structure from columns
            self._extract_section_subject_structure()
            
            # Step 3: Validate structure
            self._validate_structure()
            
            # Step 4: Transform to heatmap records
            self._transform_to_heatmap()
            
            # Step 5: Validate all records
            self._validate_records()
            
            return self.transformation_results, self.validation_errors
            
        except HeatmapTransformationError as e:
            self.validation_errors.append(str(e))
            return [], self.validation_errors
    
    def _parse_input(self):
        """Parse input into DataFrame"""
        if isinstance(self.excel_data, pd.DataFrame):
            self.df = self.excel_data.copy()
        elif isinstance(self.excel_data, dict):
            self.df = pd.DataFrame(self.excel_data).T
        else:
            raise HeatmapTransformationError("Input must be pandas DataFrame or dict")
        
        # Remove empty rows/columns
        self.df = self.df.dropna(how='all')
        self.df = self.df.dropna(axis=1, how='all')
        
        if self.df.empty:
            raise HeatmapTransformationError("Input data is empty")
    
    def _extract_section_subject_structure(self):
        """Extract section-subject pairs from column names"""
        for col in self.df.columns:
            col_str = str(col).strip()
            
            # Parse "SECTION - SUBJECT" format
            if " - " in col_str:
                parts = col_str.split(" - ", 1)
                if len(parts) == 2:
                    section = parts[0].strip()
                    subject = parts[1].strip()
                    
                    if section not in self.section_subject_mapping:
                        self.section_subject_mapping[section] = set()
                    self.section_subject_mapping[section].add(subject)
    
    def _validate_structure(self):
        """Validate that input has required structure"""
        if not self.section_subject_mapping:
            raise HeatmapTransformationError(
                "No section-subject pairs found. Expected columns like 'PCMB A - MATHS'"
            )
        
        # Check if all required metrics are present
        required_metrics = self.PASS_METRICS + [self.TOTAL_METRIC]
        missing_metrics = [m for m in required_metrics if m not in self.df.index]
        if missing_metrics:
            raise HeatmapTransformationError(
                f"Missing required metrics: {missing_metrics}"
            )
    
    def _transform_to_heatmap(self):
        """Transform to flat heatmap records"""
        for section, subjects in self.section_subject_mapping.items():
            # Determine stream from section name
            stream = self._get_stream(section)
            if stream is None:
                self.validation_errors.append(f"Unknown stream for section: {section}")
                continue
            
            for subject in subjects:
                col_key = f"{section} - {subject}"
                
                try:
                    # Extract values
                    distinction = self._get_value(col_key, "Distinction")
                    first_class = self._get_value(col_key, "First Class")
                    second_class = self._get_value(col_key, "Second Class")
                    pass_class = self._get_value(col_key, "Pass Class")
                    fail = self._get_value(col_key, self.FAIL_METRIC, default=0)
                    total = self._get_value(col_key, self.TOTAL_METRIC)
                    
                    # Validate total
                    if total <= 0 or pd.isna(total):
                        self.validation_errors.append(
                            f"Invalid total for {section} - {subject}: {total}"
                        )
                        continue
                    
                    # Calculate pass %
                    pass_count = distinction + first_class + second_class + pass_class
                    pass_percentage = round((pass_count / total) * 100, 2)
                    
                    # Create heatmap record with both pass% and grade distribution
                    record = {
                        "section": section,
                        "subject": subject,
                        "pass_percentage": pass_percentage,
                        "fail": int(fail) if not pd.isna(fail) else 0,
                        "total": int(total),
                        "stream": stream,
                        # Grade distribution data
                        "distinction": int(distinction) if not pd.isna(distinction) else 0,
                        "i class": int(first_class) if not pd.isna(first_class) else 0,
                        "ii class": int(second_class) if not pd.isna(second_class) else 0,
                        "iii class": int(pass_class) if not pd.isna(pass_class) else 0,
                        "centums": 0,  # Not tracked separately, may be subset of distinction
                    }
                    
                    self.transformation_results.append(record)
                    
                except Exception as e:
                    self.validation_errors.append(
                        f"Error processing {section} - {subject}: {str(e)}"
                    )
    
    def _get_value(self, col_key: str, metric: str, default=None) -> float:
        """Safely extract numeric value from DataFrame"""
        try:
            if metric not in self.df.index:
                if default is not None:
                    return default
                raise ValueError(f"Metric '{metric}' not found")
            
            value = self.df.loc[metric, col_key]
            
            if pd.isna(value):
                if default is not None:
                    return default
                return 0
            
            return float(value)
        except (KeyError, ValueError, TypeError):
            if default is not None:
                return default
            return 0
    
    def _get_stream(self, section: str) -> str or None:
        """Determine stream from section name"""
        if section in self.SCIENCE_SECTIONS:
            return "Science"
        elif section in self.COMMERCE_SECTIONS:
            return "Commerce"
        return None
    
    def _validate_records(self):
        """Validate all transformed records"""
        for record in self.transformation_results:
            # Validate pass percentage is 0-100
            if not (0 <= record["pass_percentage"] <= 100):
                self.validation_errors.append(
                    f"Invalid pass % for {record['section']} - {record['subject']}: "
                    f"{record['pass_percentage']}"
                )
            
            # Validate total > 0
            if record["total"] <= 0:
                self.validation_errors.append(
                    f"Invalid total for {record['section']} - {record['subject']}: "
                    f"{record['total']}"
                )
