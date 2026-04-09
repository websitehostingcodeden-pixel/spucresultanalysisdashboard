"""
Extended test data for Phase 2 - Full Science section heatmap
All 6 Science sections with multiple subjects and varied pass percentages
"""

import pandas as pd
from io import StringIO

# ===== PHASE 2: FULL SCIENCE STREAM HEATMAP =====
# 6 Sections × 5 Subjects = 30 records

SCIENCE_HEATMAP_CSV = """Metric,PCMB A - MATHS,PCMB A - ENG,PCMB A - PHY,PCMB A - CHM,PCMB A - BIO,PCMB B - MATHS,PCMB B - ENG,PCMB B - PHY,PCMB B - CHM,PCMB B - BIO,PCMB C - MATHS,PCMB C - ENG,PCMB C - PHY,PCMB C - CHM,PCMB C - BIO,PCMB D - MATHS,PCMB D - ENG,PCMB D - PHY,PCMB D - CHM,PCMB D - BIO,PCMC F - MATHS,PCMC F - ENG,PCMC F - PHY,PCMC F - CHM,PCMC F - BIO,PCME E - MATHS,PCME E - ENG,PCME E - PHY,PCME E - CHM,PCME E - BIO
Distinction,22,20,18,19,17,19,17,15,16,14,21,18,16,18,15,18,16,14,15,13,20,19,17,18,16,15,13,12,14,11
First Class,19,18,16,17,16,17,16,14,15,13,18,16,15,17,14,16,15,13,14,12,18,17,15,16,15,14,12,11,13,10
Second Class,6,8,10,8,9,8,9,11,9,10,6,10,12,8,12,10,11,13,11,14,8,9,11,9,10,14,15,17,15,18
Pass Class,5,6,8,2,4,2,4,6,4,5,7,8,11,9,10,4,6,8,6,8,4,5,7,5,6,9,12,14,12,14
Fail,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
Total,52,52,52,46,46,46,46,46,44,42,52,52,52,52,51,48,48,48,46,47,50,50,50,48,47,52,52,54,54,53
"""

COMMERCE_HEATMAP_CSV = """Metric,CEBA G1 - MATHS,CEBA G1 - ENG,CEBA G1 - ACC,CEBA G2 - MATHS,CEBA G2 - ENG,CEBA G2 - ACC,CEBA/CSBA G3 - MATHS,CEBA/CSBA G3 - ENG,CEBA/CSBA G3 - ACC,SEBA G4 - MATHS,SEBA G4 - ENG,SEBA G4 - ACC,PEBA G6 - MATHS,PEBA G6 - ENG,PEBA G6 - ACC,MSBA/MEBA G5 - MATHS,MSBA/MEBA G5 - ENG,MSBA/MEBA G5 - ACC
Distinction,12,14,11,8,10,7,6,8,5,5,7,4,4,5,3,7,9,6
First Class,32,30,33,28,26,30,24,22,28,20,18,24,18,16,20,22,20,24
Second Class,14,16,14,14,16,16,18,20,14,16,18,16,14,16,18,16,14,12
Pass Class,2,4,6,4,6,8,5,8,10,6,8,10,8,10,12,4,6,8
Fail,0,0,0,3,2,1,2,1,2,1,1,2,2,1,2,2,1,2
Total,60,64,64,57,60,62,55,59,59,48,52,56,46,48,55,51,50,52
"""


def get_science_heatmap_data() -> pd.DataFrame:
    """Get Science stream heatmap (6 sections × 5 subjects)"""
    df = pd.read_csv(StringIO(SCIENCE_HEATMAP_CSV))
    df = df.set_index("Metric")
    return df


def get_commerce_heatmap_data() -> pd.DataFrame:
    """Get Commerce stream heatmap (6 sections × 3 subjects)"""
    df = pd.read_csv(StringIO(COMMERCE_HEATMAP_CSV))
    df = df.set_index("Metric")
    return df


def get_all_heatmap_data(stream: str = "Science") -> pd.DataFrame:
    """Get heatmap for specified stream"""
    if stream.lower() == "science":
        return get_science_heatmap_data()
    elif stream.lower() == "commerce":
        return get_commerce_heatmap_data()
    else:
        raise ValueError(f"Unknown stream: {stream}")


# ===== EXPECTED RESULTS FOR VERIFICATION =====

EXPECTED_SCIENCE_HEATMAP = [
    # PCMB A - All subjects
    {"section": "PCMB A", "subject": "MATHS", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB A", "subject": "ENG", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB A", "subject": "PHY", "pass_percentage": 98.08, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB A", "subject": "CHM", "pass_percentage": 95.65, "fail": 0, "total": 46, "stream": "Science"},
    {"section": "PCMB A", "subject": "BIO", "pass_percentage": 95.65, "fail": 0, "total": 46, "stream": "Science"},
    
    # PCMB B - All subjects
    {"section": "PCMB B", "subject": "MATHS", "pass_percentage": 100.0, "fail": 0, "total": 46, "stream": "Science"},
    {"section": "PCMB B", "subject": "ENG", "pass_percentage": 97.83, "fail": 0, "total": 46, "stream": "Science"},
    {"section": "PCMB B", "subject": "PHY", "pass_percentage": 95.65, "fail": 0, "total": 46, "stream": "Science"},
    {"section": "PCMB B", "subject": "CHM", "pass_percentage": 95.45, "fail": 0, "total": 44, "stream": "Science"},
    {"section": "PCMB B", "subject": "BIO", "pass_percentage": 95.24, "fail": 0, "total": 42, "stream": "Science"},
    
    # PCMB C - All subjects
    {"section": "PCMB C", "subject": "MATHS", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB C", "subject": "ENG", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB C", "subject": "PHY", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB C", "subject": "CHM", "pass_percentage": 100.0, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCMB C", "subject": "BIO", "pass_percentage": 98.04, "fail": 0, "total": 51, "stream": "Science"},
    
    # PCMB D - All subjects (some weak areas)
    {"section": "PCMB D", "subject": "MATHS", "pass_percentage": 95.83, "fail": 0, "total": 48, "stream": "Science"},
    {"section": "PCMB D", "subject": "ENG", "pass_percentage": 95.83, "fail": 0, "total": 48, "stream": "Science"},
    {"section": "PCMB D", "subject": "PHY", "pass_percentage": 95.83, "fail": 0, "total": 48, "stream": "Science"},
    {"section": "PCMB D", "subject": "CHM", "pass_percentage": 95.65, "fail": 0, "total": 46, "stream": "Science"},
    {"section": "PCMB D", "subject": "BIO", "pass_percentage": 91.49, "fail": 0, "total": 47, "stream": "Science"},
    
    # PCMC F
    {"section": "PCMC F", "subject": "MATHS", "pass_percentage": 100.0, "fail": 0, "total": 50, "stream": "Science"},
    {"section": "PCMC F", "subject": "ENG", "pass_percentage": 100.0, "fail": 0, "total": 50, "stream": "Science"},
    {"section": "PCMC F", "subject": "PHY", "pass_percentage": 100.0, "fail": 0, "total": 50, "stream": "Science"},
    {"section": "PCMC F", "subject": "CHM", "pass_percentage": 97.92, "fail": 0, "total": 48, "stream": "Science"},
    {"section": "PCMC F", "subject": "BIO", "pass_percentage": 97.87, "fail": 0, "total": 47, "stream": "Science"},
    
    # PCME E
    {"section": "PCME E", "subject": "MATHS", "pass_percentage": 96.15, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCME E", "subject": "ENG", "pass_percentage": 96.15, "fail": 0, "total": 52, "stream": "Science"},
    {"section": "PCME E", "subject": "PHY", "pass_percentage": 96.30, "fail": 0, "total": 54, "stream": "Science"},
    {"section": "PCME E", "subject": "CHM", "pass_percentage": 96.30, "fail": 0, "total": 54, "stream": "Science"},
    {"section": "PCME E", "subject": "BIO", "pass_percentage": 94.34, "fail": 0, "total": 53, "stream": "Science"},
]


if __name__ == "__main__":
    print("Phase 2 Heatmap Test Data Loading...")
    
    science_df = get_science_heatmap_data()
    print(f"✓ Science DataFrame shape: {science_df.shape}")
    print(f"✓ Columns (Section-Subject pairs): {len(science_df.columns)}")
    print(f"✓ Rows (Metrics): {list(science_df.index)}")
    print(f"\n✓ Expected Science heatmap records: {len(EXPECTED_SCIENCE_HEATMAP)}")
    print(f"✓ Unique sections: 6 (PCMB A, B, C, D, PCMC F, PCME E)")
    print(f"✓ Unique subjects per section: 5 (MATHS, ENG, PHY, CHM, BIO)")
