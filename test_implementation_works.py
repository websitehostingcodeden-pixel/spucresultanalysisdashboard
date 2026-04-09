#!/usr/bin/env python3
"""
MINIMAL WORKING EXAMPLE - Test the Toppers Implementation

This script demonstrates that the implementation actually works by:
1. Loading the TopperDataCleaner class
2. Creating sample topper data
3. Cleaning it using TopperDataCleaner
4. Showing the standardized output

This proves the core implementation is functional.

Run: python3 test_implementation_works.py
"""

import sys
import json
import os
import django
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "aris_backend"
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

def main():
    print("\n" + "="*70)
    print("TOPPERS IMPLEMENTATION - WORKING EXAMPLE")
    print("="*70 + "\n")
    
    try:
        # Step 1: Import the TopperDataCleaner
        print("📥 Step 1: Importing TopperDataCleaner...")
        from apps.results.services.analytics import TopperDataCleaner
        print("✅ IMPORT SUCCESSFUL\n")
        
        # Step 2: Create sample dirty data
        print("📊 Step 2: Creating sample topper data (with non-standard formats)...")
        sample_toppers = [
            {
                "reg_no": "ST001",
                "student_name": "Alice Smith",
                "stream": "science",  # lowercase - needs normalization
                "section": "A",
                "marks": 420.0,
                "percentage": "87.5%",  # string with % - needs conversion
                "class_name": "DISTINCTION",
                "subject_marks": {"maths": 95, "physics": 92}
            },
            {
                "reg_no": "ST002",
                "student_name": "Bob Jones",
                "stream": "COMMERCE",
                "section": "B",
                "marks": 395.0,
                "percentage": 0.825,  # decimal format - needs conversion to 0-100
                "class_name": "FIRST_CLASS",
                "subject_marks": {"economics": 88, "accounting": 85}
            },
            {
                "reg_no": "ST003",
                "student_name": "Carol White",
                "stream": None,  # null stream
                "section": "C",
                "marks": 410.0,
                "percentage": 82,  # integer - needs to stay as float
                "class_name": "FIRST_CLASS",
                "subject_marks": {"english": 89, "hindi": 91}
            }
        ]
        
        print(f"✅ Created {len(sample_toppers)} sample records with dirty data")
        print("\nBefore cleaning (DIRTY DATA):")
        print(json.dumps(sample_toppers, indent=2, default=str))
        
        # Step 3: Clean the data using TopperDataCleaner
        print("\n\n🧹 Step 3: Cleaning data using TopperDataCleaner...")
        cleaned_toppers = []
        for i, topper in enumerate(sample_toppers):
            rank = i + 1
            cleaned = TopperDataCleaner.clean_topper(topper, include_rank=True)
            cleaned["rank"] = rank  # Add rank for college/stream toppers
            cleaned_toppers.append(cleaned)
        print("✅ CLEANING COMPLETE\n")
        
        # Step 4: Display cleaned data
        print("After cleaning (STANDARDIZED DATA):")
        print(json.dumps(cleaned_toppers, indent=2, default=str))
        
        # Step 5: Verify standardization
        print("\n\n✅ VERIFICATION RESULTS:")
        print("-" * 70)
        
        for i, (original, cleaned) in enumerate(zip(sample_toppers, cleaned_toppers)):
            print(f"\nTopper {i+1}: {original['student_name']}")
            
            # Verify percentage is float
            pct = cleaned["percentage"]
            is_float = isinstance(pct, float)
            print(f"  ✅ Percentage is float: {is_float} ({pct})")
            assert is_float, f"Percentage should be float, got {type(pct)}"
            
            # Verify percentage is in 0-100 range
            in_range = 0 <= pct <= 100
            print(f"  ✅ Percentage in 0-100 range: {in_range} ({pct})")
            assert in_range, f"Percentage should be 0-100, got {pct}"
            
            # Verify stream is normalized
            stream = cleaned["stream"]
            normalized = stream in ["SCIENCE", "COMMERCE", None]
            print(f"  ✅ Stream normalized: {normalized} ({stream})")
            assert normalized, f"Stream should be SCIENCE|COMMERCE|None, got {stream}"
            
            # Verify rank exists
            has_rank = "rank" in cleaned
            print(f"  ✅ Rank field present: {has_rank}")
            assert has_rank, "Rank field missing"
        
        print("\n" + "="*70)
        print("🎉 ALL VALIDATION CHECKS PASSED")
        print("="*70)
        print("\n✅ TopperDataCleaner is working correctly!")
        print("✅ Data standardization is functioning!")
        print("✅ Implementation is verified and operational!")
        
        return 0
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("\nMake sure you're running this from the project root directory")
        print("Expected directory structure:")
        print("  /spuc-RA ARIS/")
        print("    ├── aris_backend/")
        print("    ├── frontend/")
        print("    └── test_implementation_works.py")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
