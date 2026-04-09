"""
Complete heatmap test data with ALL subjects for all sections
Based on actual student result data provided
"""

import pandas as pd
from io import StringIO

# SCIENCE SECTIONS - Complete data with all subjects
SCIENCE_COMPLETE_CSV = """Metric,PCMB A - KAN,PCMB A - ENG,PCMB A - PHY,PCMB A - CHE,PCMB A - MATHS,PCMB A - BIO,PCMB B - KAN,PCMB B - HIN,PCMB B - SAN,PCMB B - ENG,PCMB B - PHY,PCMB B - CHE,PCMB B - MATHS,PCMB B - BIO,PCMB C - KAN,PCMB C - HIN,PCMB C - SAN,PCMB C - ENG,PCMB C - PHY,PCMB C - CHE,PCMB C - MATHS,PCMB C - BIO,PCMB C - C.SCI,PCMB C - ELE,PCMB D - KAN,PCMB D - HIN,PCMB D - SAN,PCMB D - ENG,PCMB D - PHY,PCMB D - CHE,PCMB D - MATHS,PCMB D - BIO,PCMC F - KAN,PCMC F - HIN,PCMC F - SAN,PCMC F - ENG,PCMC F - PHY,PCMC F - CHE,PCMC F - MATHS,PCMC F - C.SCI,PCME E - KAN,PCME E - HIN,PCME E - SAN,PCME E - ENG,PCME E - PHY,PCME E - CHE,PCME E - MATHS,PCME E - ELEC
Distinction,10,36,4,10,22,3,1,1,5,17,1,1,9,1,34,12,14,70,48,48,57,31,19,6,26,3,3,58,12,10,28,11,5,2,4,37,7,8,15,23,3,1,5,31,4,4,6,14
First Class,29,16,23,21,19,27,14,6,15,35,17,18,26,15,5,3,1,0,21,21,13,10,1,0,18,5,3,7,32,35,32,35,15,6,4,20,23,26,34,30,8,4,7,15,14,12,21,20
Second Class,9,0,7,13,6,8,1,3,3,0,13,21,9,19,1,0,0,0,1,1,0,1,0,0,3,2,0,0,15,13,2,12,12,1,0,0,14,17,7,3,3,1,2,0,7,14,12,11
Pass Class,4,0,16,6,5,12,2,2,1,2,21,11,9,17,0,0,0,0,0,0,0,2,0,0,0,1,0,0,4,5,3,5,7,1,0,0,13,6,1,1,8,2,2,0,19,14,7,1
Fail,0,0,2,2,0,2,1,0,0,1,3,4,2,3,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,2,0,2,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0
Total,52,52,52,52,52,52,18,12,22,55,55,55,55,55,54,18,18,70,70,70,70,70,20,6,48,11,6,65,65,65,65,65,47,10,8,57,57,57,57,57,22,8,16,46,46,46,46,46
"""

# COMMERCE SECTIONS - Complete data with all subjects
COMMERCE_COMPLETE_CSV = """Metric,CEBA G1 - KAN,CEBA G1 - HIN,CEBA G1 - SAN,CEBA G1 - ENG,CEBA G1 - ECO,CEBA G1 - B.STU,CEBA G1 - ACC,CEBA G1 - C.SCI,CEBA G2 - KAN,CEBA G2 - ENG,CEBA G2 - ECO,CEBA G2 - B.STU,CEBA G2 - ACC,CEBA G2 - C.SCI,CEBA G3 - KAN,CEBA G3 - HIN,CEBA G3 - SAN,CEBA G3 - ENG,CEBA G3 - ECO,CEBA G3 - B.STU,CEBA G3 - ACC,CEBA G3 - C.SCI,CSBA G3 - KAN,CSBA G3 - HIN,CSBA G3 - SAN,CSBA G3 - ENG,CSBA G3 - B.STU,CSBA G3 - ACC,CSBA G3 - STATS,CSBA G3 - C.SCI,SEBA G4 - KAN,SEBA G4 - HIN,SEBA G4 - SAN,SEBA G4 - ENG,SEBA G4 - ECO,SEBA G4 - B.STU,SEBA G4 - ACC,SEBA G4 - STATS,PEBA G6 - KAN,PEBA G6 - HIN,PEBA G6 - SAN,PEBA G6 - ENG,PEBA G6 - ECO,PEBA G6 - B.STU,PEBA G6 - P.SCI,PEBA G6 - ACC,MSBA G5 - KAN,MSBA G5 - HIN,MSBA G5 - SAN,MSBA G5 - ENG,MSBA G5 - B.STU,MSBA G5 - ACC,MSBA G5 - STATS,MSBA G5 - B.MATHS,MEBA G5 - KAN,MEBA G5 - HIN,MEBA G5 - SAN,MEBA G5 - ENG,MEBA G5 - ECO,MEBA G5 - B.STU,MEBA G5 - ACC,MEBA G5 - B.MATHS
Distinction,10,7,4,45,24,21,27,31,2,13,1,3,3,11,0,3,0,7,4,5,4,3,13,1,2,13,10,9,19,16,9,0,0,20,10,11,20,34,1,1,0,9,2,6,12,11,0,2,2,4,4,36,21,25,28,18
First Class,20,9,4,26,34,35,40,34,26,47,25,16,40,41,1,3,0,21,4,7,10,7,11,6,1,12,14,17,12,12,24,3,3,43,26,21,35,24,5,2,2,27,16,22,16,19,0,0,10,7,1,6,13,11,12,6
Second Class,8,1,1,0,8,12,3,5,9,7,14,11,14,8,0,2,1,6,5,6,8,10,0,0,0,4,2,5,4,5,12,4,2,9,17,4,9,9,6,1,2,9,8,8,10,14,0,0,4,0,0,0,2,2,1,3
Pass Class,6,1,0,0,5,3,1,1,32,2,29,39,12,9,5,16,3,0,21,16,12,14,0,1,0,6,9,4,0,2,12,4,0,1,20,37,9,6,19,8,1,4,22,12,11,5,2,0,2,0,1,0,3,0,0,3
Fail,0,0,0,0,2,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,1,0,1,0,0,0,1,0,2,0,0,0,0,0,0,0,0,0,0,2
Total,44,18,9,71,71,71,71,71,69,69,69,69,69,69,6,24,4,34,34,34,34,34,24,8,3,35,35,35,35,35,57,11,5,73,73,73,73,73,31,12,5,49,48,48,49,49,2,2,22,11,6,42,49,38,48,17
"""

def get_science_complete_data() -> pd.DataFrame:
    """Get complete Science stream data (6 sections × all subjects)"""
    df = pd.read_csv(StringIO(SCIENCE_COMPLETE_CSV))
    df = df.set_index("Metric")
    return df


def get_commerce_complete_data() -> pd.DataFrame:
    """Get complete Commerce stream data (6 sections × all subjects)"""
    df = pd.read_csv(StringIO(COMMERCE_COMPLETE_CSV))
    df = df.set_index("Metric")
    return df


def get_complete_heatmap_data(stream: str = "Science") -> pd.DataFrame:
    """Get complete heatmap data for specified stream"""
    if stream.lower() == "science":
        return get_science_complete_data()
    elif stream.lower() == "commerce":
        return get_commerce_complete_data()
    else:
        raise ValueError(f"Unknown stream: {stream}")
