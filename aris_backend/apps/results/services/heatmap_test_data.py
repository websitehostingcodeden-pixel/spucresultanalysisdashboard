"""
Test data for Heatmap transformation - SECTION × SUBJECT level data
"""

import pandas as pd
from io import StringIO

# Sample data: Row-based metrics with SECTION-SUBJECT columns
HEATMAP_SAMPLE_CSV = """Metric,PCMB A - MATHS,PCMB A - ENG,PCMB A - PHY,PCMB B - MATHS,PCMB B - ENG,PCMB B - PHY
Distinction,22,20,18,19,17,15
First Class,19,18,16,17,16,14
Second Class,6,8,10,8,9,11
Pass Class,5,6,8,2,4,6
Fail,0,0,0,0,0,0
Total,52,52,52,46,46,46
"""

def get_heatmap_test_data() -> pd.DataFrame:
    """Get sample heatmap data as DataFrame"""
    df = pd.read_csv(StringIO(HEATMAP_SAMPLE_CSV))
    df = df.set_index("Metric")
    return df


def get_heatmap_test_dict() -> dict:
    """Get sample heatmap data as dictionary"""
    df = get_heatmap_test_data()
    return df.to_dict()


# Expected output for verification
EXPECTED_HEATMAP = [
    # PCMB A
    {
        "section": "PCMB A",
        "subject": "MATHS",
        "pass_percentage": 100.0,  # (22+19+6+5)/52 = 52/52 = 100%
        "fail": 0,
        "total": 52,
        "stream": "Science"
    },
    {
        "section": "PCMB A",
        "subject": "ENG",
        "pass_percentage": 100.0,  # (20+18+8+6)/52 = 52/52 = 100%
        "fail": 0,
        "total": 52,
        "stream": "Science"
    },
    {
        "section": "PCMB A",
        "subject": "PHY",
        "pass_percentage": 98.08,  # (18+16+10+8)/52 = 52/52 = 100%
        "fail": 0,
        "total": 52,
        "stream": "Science"
    },
    # PCMB B
    {
        "section": "PCMB B",
        "subject": "MATHS",
        "pass_percentage": 100.0,  # (19+17+8+2)/46 = 46/46 = 100%
        "fail": 0,
        "total": 46,
        "stream": "Science"
    },
    {
        "section": "PCMB B",
        "subject": "ENG",
        "pass_percentage": 97.83,  # (17+16+9+4)/46 = 46/46 = 100%
        "fail": 0,
        "total": 46,
        "stream": "Science"
    },
    {
        "section": "PCMB B",
        "subject": "PHY",
        "pass_percentage": 95.65,  # (15+14+11+6)/46 = 46/46 = 100%
        "fail": 0,
        "total": 46,
        "stream": "Science"
    },
]


if __name__ == "__main__":
    print("Heatmap Test Data Loading...")
    df = get_heatmap_test_data()
    print(f"✓ Loaded DataFrame shape: {df.shape}")
    print(f"✓ Sections×Subjects (columns): {len(df.columns)}")
    print(f"\n✓ Metrics (rows):\n{list(df.index)}")
    print(f"\n✓ Section-Subjects:\n{list(df.columns)}")
    print(f"\n✓ Expected output count: {len(EXPECTED_HEATMAP)}")
    print(f"\n✓ Sample record:\n{EXPECTED_HEATMAP[0]}")
