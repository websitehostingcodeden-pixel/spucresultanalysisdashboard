import pandas as pd
import os

# Create a real Excel file with 6 subjects that matches the whitelist
data = {
    'REG_NO': ['TEST001', 'TEST002'],
    'STUDENT_NAME': ['Student One', 'Student Two'],
    'STREAM': ['SCIENCE', 'COMMERCE'],
    'SECTION': ['A', 'B'],
    'ENGLISH': [95, 90],
    'PHYSICS': [98, 0],  # 0 for commerce
    'CHEMISTRY': [96, 0],  # 0 for commerce
    'MATHEMATICS': [99, 92],
    'BIOLOGY': [97, 0],  # 0 for commerce
    'SOCIAL_STUDIES': [88, 85],
    'ECONOMICS': [0, 94],  # 0 for science
    'BUSINESS_STUDIES': [0, 93],  # 0 for science
    'ACCOUNTING': [0, 91],  # 0 for science
    'HINDI': [0, 89],  # 0 for science
    'GRAND_TOTAL': [573, 534],
    'PERCENTAGE': [95.5, 89.0],
    'RESULT_CLASS': ['DISTINCTION', 'FIRST_CLASS']
}

df = pd.DataFrame(data)

# Save as Excel
output_file = 'test_6_subjects_real.xlsx'
df.to_excel(output_file, index=False, sheet_name='Results')

print(f"Created: {output_file}")
print(f"Shape: {df.shape}")
print(f"\nColumns with subject marks:")
for col in df.columns:
    col_lower = col.lower()
    if any(kw in col_lower for kw in ['physics', 'chemistry', 'biology', 'english', 'math', 'social', 'economics', 'business', 'accounting', 'hindi']):
        print(f"  - {col}")

print(f"\nRow 1 non-zero subject values:")
row1 = df.iloc[0]
for col in df.columns:
    col_lower = col.lower()
    if any(kw in col_lower for kw in ['physics', 'chemistry', 'biology', 'english', 'math', 'social', 'economics', 'business', 'accounting', 'hindi']):
        val = row1[col]
        if val > 0:
            print(f"  - {col}: {val}")
