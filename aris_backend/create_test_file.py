import pandas as pd
import numpy as np
from datetime import datetime

# Create test Excel file with REAL header from user
data_science = {
    'SR.NO.': [1, 2, 3, 4, 5],
    'REG NO': ['17SC001', '17SC002', '17SC003', '17SC004', '17SC005'],
    'SATS NO.': ['SAT001', 'SAT002', 'SAT003', 'SAT004', 'SAT005'],
    'ENROLLMENT NO.': ['ENR001', 'ENR002', 'ENR003', 'ENR004', 'ENR005'],
    'STUDENT NAME': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'SECT': ['A', 'A', 'B', 'B', 'A'],
    'K/H/S': ['K', 'H', 'S', 'K', 'H'],  # Language - non-numeric
    'ENGLISH': [85.0, 78.0, 92.0, 68.0, 88.0],
    'SUB1': [90.0, 82.0, 88.0, 75.0, 91.0],
    'SUB2': [88.0, 80.0, 85.0, 72.0, 89.0],
    'SUB3': [92.0, 85.0, 90.0, 78.0, 93.0],
    'SUB4': [86.0, 79.0, 87.0, 70.0, 85.0],
    'PART-1 TOTAL': [355.0, 324.0, 360.0, 293.0, 356.0],
    'PART-2 TOTAL': [200.0, 180.0, 210.0, 150.0, 205.0],
    'GRAND TOTAL': [555.0, 504.0, 570.0, 443.0, 561.0],
    'RESULT': ['PASS', 'PASS', 'PASS', 'PASS', 'PASS'],
    'CLASS': ['FIRST', 'FIRST', 'FIRST', 'SECOND', 'FIRST'],
    'PERCENTAGE': [92.5, 84.0, 95.0, 73.8, 93.5]
}

# Create test mismatches to trigger validation warning
data_science['PERCENTAGE'][2] = 100.0  # Mismatch: should be 95% not 100%
data_science['SECT'][1] = 'C'  # Section mismatch: SECT=C but REG NO says A
data_science['PART-1 TOTAL'][4] = 360.0  # Mismatch: 360 + 205 ≠ 561

df_science = pd.DataFrame(data_science)

# Commerce stream
data_commerce = {
    'SR.NO.': [6, 7, 8],
    'REG NO': ['17CO001', '17CO002', '17CO003'],
    'SATS NO.': ['SAT006', 'SAT007', 'SAT008'],
    'ENROLLMENT NO.': ['ENR006', 'ENR007', 'ENR008'],
    'STUDENT NAME': ['Frank', 'Grace', 'Henry'],
    'SECT': ['X', 'X', 'Y'],
    'K/H/S': ['H', 'S', 'K'],
    'ENGLISH': [82.0, 88.0, 75.0],
    'SUB1': [85.0, 90.0, 72.0],
    'SUB2': [80.0, 87.0, 70.0],
    'SUB3': [88.0, 92.0, 78.0],
    'SUB4': [83.0, 89.0, 73.0],
    'PART-1 TOTAL': [336.0, 359.0, 295.0],
    'PART-2 TOTAL': [150.0, 180.0, 130.0],
    'GRAND TOTAL': [486.0, 539.0, 425.0],
    'RESULT': ['PASS', 'PASS', 'FAIL'],
    'CLASS': ['SECOND', 'FIRST', 'FAIL'],
    'PERCENTAGE': [97.2, 107.8, 85.0]  # 97.2=invalid (>100), 107.8=invalid
}

df_commerce = pd.DataFrame(data_commerce)

# Write to Excel
with pd.ExcelWriter('test_edge_cases.xlsx', engine='openpyxl') as writer:
    df_science.to_excel(writer, sheet_name='SCIENCE', index=False)
    df_commerce.to_excel(writer, sheet_name='COMMERCE', index=False)

print("✓ Created test_edge_cases.xlsx with:")
print(f"  - {len(df_science)} SCIENCE records (with validation issues)")
print(f"  - {len(df_commerce)} COMMERCE records (with validation issues)")
print("\nValidation issues included:")
print("  1. Percentage mismatches (>100%, calculated vs provided)")
print("  2. Section mismatches (SECT vs extracted from REG NO)")
print("  3. Part total mismatches (PART-1 + PART-2 ≠ GRAND TOTAL)")
print("  4. Alternate identifiers (SATS NO, ENROLLMENT NO)")
print("  5. Non-numeric columns (K/H/S language field)")
print("  6. Duplicate semantics (RESULT vs CLASS)")
