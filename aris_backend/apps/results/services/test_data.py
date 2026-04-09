"""
Test data for Section Performance transformation.

Raw Excel structure (row-based):
- Rows: Metrics (Enrolled, Absent, Appeared, Distinction, etc.)
- Columns: Section names (PCMB A, PCMB B, ..., MSBA/MEBA G5)
"""

import pandas as pd
from io import StringIO

# Raw data as it appears in Excel (row-based metrics)
RAW_EXCEL_CSV = """Metric,PCMB A,PCMB B,PCMB C,PCMB D,PCMC F,PCME E,CEBA G1,CEBA G2,CEBA G3,CSBA G3,SEBA G4,PEBA G6,MSBA G5,MEBA G5
Enrolled,52,48,55,60,50,58,45,50,40,35,48,46,30,32
Absent,0,2,1,1,0,2,3,1,1,1,0,1,1,0
Appeared,52,46,54,59,50,56,42,49,39,34,48,45,29,32
Distinction,8,7,9,11,8,10,5,6,3,5,6,5,4,3
First Class,30,28,32,35,29,33,25,29,14,12,28,26,12,14
Second Class,12,10,12,12,12,12,12,14,12,10,14,14,8,10
Pass Class,2,1,1,1,1,1,0,0,8,5,0,0,3,3
Detained,0,0,0,0,0,0,0,0,2,2,0,0,2,2
Promoted,50,45,53,58,49,55,42,49,37,32,48,45,27,25
"""

def load_raw_excel_data() -> dict:
    """Load raw Excel data from CSV format"""
    df = pd.read_csv(StringIO(RAW_EXCEL_CSV))
    
    # Set Metric column as index (rows are metrics)
    df = df.set_index("Metric")
    
    # Convert to dict format expected by SectionTransformer
    data_dict = {}
    for row_idx in df.index:
        data_dict[row_idx] = df.loc[row_idx].to_dict()
    
    return data_dict


def get_raw_dataframe() -> pd.DataFrame:
    """Get raw Excel data as DataFrame (row-based, no index)"""
    df = pd.read_csv(StringIO(RAW_EXCEL_CSV))
    df = df.set_index("Metric")
    return df


def get_raw_dict() -> dict:
    """Get raw Excel data as dictionary"""
    df = pd.read_csv(StringIO(RAW_EXCEL_CSV))
    df = df.set_index("Metric")
    
    # Return as dict where keys are metrics, values are dicts of sections
    return df.to_dict()


# Expected output for testing
EXPECTED_SECTIONS = [
    {"section": "PCMB A", "stream": "Science", "enrolled": 52, "absent": 0, "appeared": 52, 
     "distinction": 8, "first_class": 30, "second_class": 12, "pass_class": 2, "detained": 0, "promoted": 50, "pass_percentage": 96.15},
    {"section": "PCMB B", "stream": "Science", "enrolled": 48, "absent": 2, "appeared": 46,
     "distinction": 7, "first_class": 28, "second_class": 10, "pass_class": 1, "detained": 0, "promoted": 45, "pass_percentage": 97.83},
    {"section": "PCMB C", "stream": "Science", "enrolled": 55, "absent": 1, "appeared": 54,
     "distinction": 9, "first_class": 32, "second_class": 12, "pass_class": 1, "detained": 0, "promoted": 53, "pass_percentage": 98.15},
    {"section": "PCMB D", "stream": "Science", "enrolled": 60, "absent": 1, "appeared": 59,
     "distinction": 11, "first_class": 35, "second_class": 12, "pass_class": 1, "detained": 0, "promoted": 58, "pass_percentage": 98.31},
    {"section": "PCMC F", "stream": "Science", "enrolled": 50, "absent": 0, "appeared": 50,
     "distinction": 8, "first_class": 29, "second_class": 12, "pass_class": 1, "detained": 0, "promoted": 49, "pass_percentage": 100.0},
    {"section": "PCME E", "stream": "Science", "enrolled": 58, "absent": 2, "appeared": 56,
     "distinction": 10, "first_class": 33, "second_class": 12, "pass_class": 1, "detained": 0, "promoted": 55, "pass_percentage": 100.0},
    {"section": "CEBA G1", "stream": "Commerce", "enrolled": 45, "absent": 3, "appeared": 42,
     "distinction": 5, "first_class": 25, "second_class": 12, "pass_class": 0, "detained": 0, "promoted": 42, "pass_percentage": 100.0},
    {"section": "CEBA G2", "stream": "Commerce", "enrolled": 50, "absent": 1, "appeared": 49,
     "distinction": 6, "first_class": 29, "second_class": 14, "pass_class": 0, "detained": 0, "promoted": 49, "pass_percentage": 100.0},
    {"section": "CEBA G3", "stream": "Commerce", "enrolled": 40, "absent": 1, "appeared": 39,
     "distinction": 3, "first_class": 14, "second_class": 12, "pass_class": 8, "detained": 2, "promoted": 37, "pass_percentage": 95.0},
    {"section": "CSBA G3", "stream": "Commerce", "enrolled": 35, "absent": 1, "appeared": 34,
     "distinction": 5, "first_class": 12, "second_class": 10, "pass_class": 5, "detained": 2, "promoted": 32, "pass_percentage": 94.1},
    {"section": "SEBA G4", "stream": "Commerce", "enrolled": 48, "absent": 0, "appeared": 48,
     "distinction": 6, "first_class": 28, "second_class": 14, "pass_class": 0, "detained": 0, "promoted": 48, "pass_percentage": 100.0},
    {"section": "PEBA G6", "stream": "Commerce", "enrolled": 46, "absent": 1, "appeared": 45,
     "distinction": 5, "first_class": 26, "second_class": 14, "pass_class": 0, "detained": 0, "promoted": 45, "pass_percentage": 100.0},
    {"section": "MSBA G5", "stream": "Commerce", "enrolled": 30, "absent": 1, "appeared": 29,
     "distinction": 4, "first_class": 12, "second_class": 8, "pass_class": 3, "detained": 2, "promoted": 27, "pass_percentage": 93.1},
    {"section": "MEBA G5", "stream": "Commerce", "enrolled": 32, "absent": 0, "appeared": 32,
     "distinction": 3, "first_class": 14, "second_class": 10, "pass_class": 3, "detained": 2, "promoted": 25, "pass_percentage": 90.6},
]


if __name__ == "__main__":
    print("Test data loading...")
    df = get_raw_dataframe()
    print(f"Loaded DataFrame shape: {df.shape}")
    print(f"Sections found: {len(df.columns)}")
    print(f"\nMetrics (rows):\n{df.index.tolist()}")
    print(f"\nSections (columns):\n{df.columns.tolist()}")
