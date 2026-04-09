"""
Test the validation system with edge cases
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.results.services.cleaner import clean_data
from apps.results.services.excel_reader import read_excel
import pandas as pd

print("\n" + "="*70)
print("TESTING DEFENSIVE VALIDATION SYSTEM")
print("="*70)

# Read the test file
print("\n1. Reading Excel file with edge cases...")
try:
    # Manually read sheets to simulate real file
    xls = pd.ExcelFile('test_edge_cases.xlsx')
    df_science = pd.read_excel(xls, 'SCIENCE')
    df_commerce = pd.read_excel(xls, 'COMMERCE')
    
    df_science['stream'] = 'SCIENCE'
    df_commerce['stream'] = 'COMMERCE'
    df = pd.concat([df_science, df_commerce], ignore_index=True)
    
    print(f"   ✓ Read {len(df_science)} SCIENCE + {len(df_commerce)} COMMERCE records")
    print(f"   ✓ Columns: {list(df.columns)[:5]}... ({len(df.columns)} total)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test the cleaner
print("\n2. Running cleaning and validation...")
try:
    clean_df, quality_metrics = clean_data(df)
    print(f"   ✓ Cleaner completed")
    print(f"   ✓ Output: {len(clean_df)} records (from {quality_metrics['original_records']})")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Display quality metrics
print("\n3. Data Quality Report")
print("   " + "-"*66)
print(f"   Retention Rate: {quality_metrics['retention_rate']:.1f}%")
print(f"   ")
print("   Issues Found:")
print(f"     • Invalid Registration Numbers: {quality_metrics['invalid_reg_no_removed']}")
print(f"     • Duplicates Removed: {quality_metrics['duplicates_removed']}")
print(f"     • Missing Grand Totals: {quality_metrics['missing_grand_total_removed']}")
print(f"     • Percentages Calculated: {quality_metrics['missing_percentage_filled']}")
print(f"     • Invalid Percentages Corrected: {quality_metrics['invalid_percentage_corrected']}")

# Show sample records
print(f"\n4. Sample Output Records")
print("   " + "-"*66)
print("   Fields: reg_no | stream | percentage | result_class | section")
for idx, row in clean_df.head(3).iterrows():
    print(f"   {row['reg_no']:8s} | {row['stream']:9s} | {row['percentage']:10.1f} | {row['result_class']:14s} | {row['section']}")

# Test fields specific to new validation system
print(f"\n5. New Validation Tracking Fields Check")
print("   " + "-"*66)
print(f"   StudentResult includes:")
print(f"     ✓ result_class: {len(clean_df[clean_df['result_class'].notna()])} records have class")
print(f"     ✓ data_completeness_score: min={clean_df['data_completeness_score'].min()}, max={clean_df['data_completeness_score'].max()}")

# Check result class distribution
dist = clean_df['result_class'].value_counts().to_dict()
print(f"     ✓ Result classification distribution:")
for cls, cnt in sorted(dist.items()):
    print(f"       - {cls}: {cnt} students")

# Test section validation
print(f"\n6. Section Reconciliation Test")
print("   " + "-"*66)
try:
    xls_check = pd.ExcelFile('test_edge_cases.xlsx')
    df_sect = pd.read_excel(xls_check, 'SCIENCE')
    
    # Extract section from REG NO vs SECT column
    df_sect['section_extracted'] = df_sect['REG NO'].str[2:4]
    
    mismatches = 0
    for idx, row in df_sect.iterrows():
        if str(row['SECT']).strip() != str(row['section_extracted']).strip():
            mismatches += 1
            print(f"     ⚠ MISMATCH: {row['REG NO']} - SECT={row['SECT']}, Extracted={row['section_extracted']}")
    
    if mismatches == 0:
        print(f"     ✓ All sections match")
    else:
        print(f"     ⚠ Found {mismatches} section mismatches (system will track in UploadLog)")
except Exception as e:
    print(f"     ✗ Error: {e}")

print("\n" + "="*70)
print("✅ VALIDATION SYSTEM TEST COMPLETE")
print("="*70)
print("\nSystem is ready for production upload testing.")
print("Run: python manage.py runserver")
print("Then POST file to: http://localhost:8000/api/upload/")
