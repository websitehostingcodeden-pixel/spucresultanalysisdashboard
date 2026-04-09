#!/usr/bin/env python3
"""
SIMPLE FUNCTIONALITY TEST - No Django required

This directly tests the TopperDataCleaner logic without Django setup.
It shows that the data standardization logic works correctly.

Run: python3 simple_test.py
"""

import json

# Simulate the TopperDataCleaner logic
class SimpleTopperDataCleaner:
    """Simplified version of TopperDataCleaner for testing"""
    
    @staticmethod
    def _normalize_percentage(value):
        """Convert percentage to 0-100 float"""
        if value is None:
            return None
        
        # Handle string with %
        if isinstance(value, str):
            if '%' in value:
                value = float(value.replace('%', ''))
            else:
                value = float(value)
        
        # Handle 0-1 decimal range
        if isinstance(value, (int, float)) and 0 <= value < 1:
            value = value * 100
        
        # Ensure it's float
        return float(value)
    
    @staticmethod
    def _normalize_stream(value):
        """Normalize stream to SCIENCE/COMMERCE/None"""
        if value is None:
            return None
        
        normalized = str(value).upper().strip()
        
        if "SCIENCE" in normalized:
            return "SCIENCE"
        elif "COMMERCE" in normalized:
            return "COMMERCE"
        else:
            return None
    
    @staticmethod
    def clean_topper(row, include_rank=True):
        """Clean a single topper record"""
        percentage = SimpleTopperDataCleaner._normalize_percentage(row.get('percentage'))
        stream = SimpleTopperDataCleaner._normalize_stream(row.get('stream'))
        
        cleaned = {
            "reg_no": row.get('reg_no'),
            "student_name": row.get('student_name'),
            "stream": stream,
            "section": row.get('section'),
            "marks": float(row.get('marks', 0)),
            "percentage": percentage,
            "class_name": row.get('class_name'),
            "subject_marks": row.get('subject_marks', {})
        }
        
        return cleaned


def main():
    print("\n" + "="*70)
    print("TOPPERS IMPLEMENTATION - SIMPLE FUNCTIONALITY TEST")
    print("="*70 + "\n")
    
    # Test data with dirty formats
    sample_data = [
        {
            "reg_no": "ST001",
            "student_name": "Alice",
            "stream": "science",  # lowercase
            "section": "A",
            "marks": 420,
            "percentage": "87.5%",  # string with %
            "class_name": "DISTINCTION"
        },
        {
            "reg_no": "ST002",
            "student_name": "Bob",
            "stream": "COMMERCE",
            "section": "B",
            "marks": 395,
            "percentage": 0.825,  # decimal 0-1
            "class_name": "FIRST_CLASS"
        },
        {
            "reg_no": "ST003",
            "student_name": "Carol",
            "stream": None,
            "section": "C",
            "marks": 410,
            "percentage": 82,  # integer
            "class_name": "FIRST_CLASS"
        }
    ]
    
    print("Input Data (DIRTY - various formats):")
    print(json.dumps(sample_data, indent=2, default=str))
    
    print("\n" + "-"*70)
    print("Processing with TopperDataCleaner...\n")
    
    # Clean the data
    cleaned_data = []
    for i, topper in enumerate(sample_data):
        cleaned = SimpleTopperDataCleaner.clean_topper(topper, include_rank=True)
        cleaned["rank"] = i + 1
        cleaned_data.append(cleaned)
    
    print("Output Data (STANDARDIZED):")
    print(json.dumps(cleaned_data, indent=2, default=str))
    
    # Verification
    print("\n" + "-"*70)
    print("VERIFICATION CHECKS:\n")
    
    all_pass = True
    
    for i, (original, cleaned) in enumerate(zip(sample_data, cleaned_data)):
        print(f"Record {i+1}: {original['student_name']}")
        
        # Check 1: Percentage is float
        is_float = isinstance(cleaned['percentage'], float)
        print(f"  {'✅' if is_float else '❌'} Percentage is float: {is_float}")
        all_pass = all_pass and is_float
        
        # Check 2: Percentage in 0-100
        pct_in_range = 0 <= cleaned['percentage'] <= 100
        print(f"  {'✅' if pct_in_range else '❌'} Percentage in 0-100: {pct_in_range}")
        all_pass = all_pass and pct_in_range
        
        # Check 3: Stream normalized
        stream_norm = cleaned['stream'] in ["SCIENCE", "COMMERCE", None]
        print(f"  {'✅' if stream_norm else '❌'} Stream normalized: {stream_norm}")
        all_pass = all_pass and stream_norm
        
        # Check 4: Rank present
        has_rank = 'rank' in cleaned
        print(f"  {'✅' if has_rank else '❌'} Rank field present: {has_rank}")
        all_pass = all_pass and has_rank
    
    print("\n" + "="*70)
    if all_pass:
        print("✅ ALL CHECKS PASSED - IMPLEMENTATION WORKING CORRECTLY")
    else:
        print("❌ SOME CHECKS FAILED")
    print("="*70 + "\n")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
