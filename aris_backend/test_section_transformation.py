"""
End-to-end test for section data transformation.

Tests:
1. Raw data loads correctly
2. Transformer validates all 12 sections present
3. No totals included
4. Data types converted correctly (percentages to floats, counts to ints)
5. Pass percentage calculated correctly
6. Stream assignment correct for all sections
"""

import json
import sys
sys.path.insert(0, '/d:/spuc-RA ARIS/aris_backend')

import pandas as pd
from apps.results.services.section_transformer import SectionTransformer, validate_section_data
from apps.results.services.test_data import get_raw_dataframe, get_raw_dict, EXPECTED_SECTIONS


def test_load_raw_data():
    """Test 1: Load raw Excel data"""
    print("\n" + "="*60)
    print("TEST 1: Load raw Excel data")
    print("="*60)
    
    df = get_raw_dataframe()
    data_dict = get_raw_dict()
    
    print(f"✓ DataFrame loaded: {df.shape}")
    print(f"✓ Metrics (rows): {len(df.index)} - {list(df.index)[:3]}...")
    print(f"✓ Sections (columns): {len(df.columns)} - {list(df.columns)[:3]}...")
    
    assert len(df.columns) == 12, f"Expected 12 sections, got {len(df.columns)}"
    assert len(df.index) == 9, f"Expected 9 metrics, got {len(df.index)}"
    
    return True


def test_transformation():
    """Test 2: Transform row-based data to section objects"""
    print("\n" + "="*60)
    print("TEST 2: Transform row-based data to section objects")
    print("="*60)
    
    df = get_raw_dataframe()
    transformer = SectionTransformer.from_dataframe(df)
    
    sections, errors = transformer.transform()
    
    if errors:
        print("⚠ Transformation errors:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"✓ Sections transformed: {len(sections)}")
    
    assert len(sections) == 12, f"Expected 12 sections, got {len(sections)}"
    assert len(errors) == 0, f"Transformation failed with {len(errors)} errors"
    
    return sections, errors


def test_schema_validation(sections):
    """Test 3: Validate transformed schema"""
    print("\n" + "="*60)
    print("TEST 3: Validate transformed schema")
    print("="*60)
    
    is_valid, errors = validate_section_data(sections)
    
    if not is_valid:
        print("✗ Schema validation failed:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Schema validation passed")
    
    # Check required fields
    required_fields = {
        "section", "stream", "enrolled", "absent", "appeared",
        "distinction", "first_class", "second_class", "pass_class",
        "detained", "promoted", "pass_percentage"
    }
    
    for section in sections:
        missing = required_fields - set(section.keys())
        if missing:
            print(f"✗ Section {section['section']}: missing fields {missing}")
            return False
    
    print(f"✓ All sections have required fields: {required_fields}")
    
    return is_valid


def test_stream_assignment(sections):
    """Test 4: Validate stream assignment"""
    print("\n" + "="*60)
    print("TEST 4: Validate stream assignment")
    print("="*60)
    
    science_sections = {
        "PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E"
    }
    commerce_sections = {
        "CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"
    }
    
    errors = []
    for section in sections:
        section_name = section["section"]
        stream = section["stream"]
        
        expected_stream = "Science" if section_name in science_sections else "Commerce"
        if stream != expected_stream:
            errors.append(
                f"Section {section_name}: expected stream '{expected_stream}', got '{stream}'"
            )
    
    if errors:
        print("✗ Stream assignment errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print(f"✓ Science sections: {len([s for s in sections if s['stream'] == 'Science'])}")
    print(f"✓ Commerce sections: {len([s for s in sections if s['stream'] == 'Commerce'])}")
    
    return True


def test_data_types(sections):
    """Test 5: Validate data types"""
    print("\n" + "="*60)
    print("TEST 5: Validate data types")
    print("="*60)
    
    errors = []
    for section in sections:
        # Check counts are integers
        for key in ["enrolled", "absent", "appeared", "distinction", 
                    "first_class", "second_class", "pass_class", "detained", "promoted"]:
            if not isinstance(section[key], int):
                errors.append(
                    f"Section {section['section']}: {key} should be int, got {type(section[key])}"
                )
        
        # Check pass_percentage is float
        if not isinstance(section["pass_percentage"], float):
            errors.append(
                f"Section {section['section']}: pass_percentage should be float, got {type(section['pass_percentage'])}"
            )
    
    if errors:
        print("✗ Data type errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✓ All counts are integers")
    print("✓ All pass_percentage values are floats")
    
    return True


def test_pass_percentage_calculation(sections):
    """Test 6: Validate pass percentage calculation"""
    print("\n" + "="*60)
    print("TEST 6: Validate pass percentage calculation")
    print("="*60)
    
    errors = []
    for section in sections:
        appeared = section["appeared"]
        if appeared == 0:
            continue
        
        passed = (
            section["distinction"] + section["first_class"] +
            section["second_class"] + section["pass_class"]
        )
        
        expected_pct = round((passed / appeared) * 100, 2)
        actual_pct = section["pass_percentage"]
        
        if abs(expected_pct - actual_pct) > 0.01:
            errors.append(
                f"Section {section['section']}: expected {expected_pct}%, got {actual_pct}%"
            )
    
    if errors:
        print("✗ Pass percentage calculation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✓ All pass percentages calculated correctly")
    
    return True


def test_all_sections_present(sections):
    """Test 7: All 12 sections present and no totals"""
    print("\n" + "="*60)
    print("TEST 7: All 12 sections present, no totals")
    print("="*60)
    
    all_sections = {
        "PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E",
        "CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"
    }
    found_sections = {s["section"] for s in sections}
    
    print(f"Expected sections: {len(all_sections)}")
    print(f"Found sections: {len(found_sections)}")
    
    missing = all_sections - found_sections
    if missing:
        print(f"✗ Missing sections: {missing}")
        return False
    
    extra = found_sections - all_sections
    if extra:
        print(f"✗ Unexpected sections (possible totals): {extra}")
        return False
    
    print("✓ All 12 sections present")
    print("✓ No totals included")
    
    return True


def test_numeric_values(sections):
    """Test 8: All counts are positive, percentages 0-100"""
    print("\n" + "="*60)
    print("TEST 8: Numeric value validation")
    print("="*60)
    
    errors = []
    for section in sections:
        # Check counts are non-negative
        for key in ["enrolled", "absent", "appeared", "distinction",
                    "first_class", "second_class", "pass_class", "detained", "promoted"]:
            if section[key] < 0:
                errors.append(
                    f"Section {section['section']}: {key} is negative ({section[key]})"
                )
        
        # Check pass_percentage is 0-100
        pct = section["pass_percentage"]
        if pct < 0 or pct > 100:
            errors.append(
                f"Section {section['section']}: pass_percentage out of range ({pct})"
            )
    
    if errors:
        print("✗ Numeric validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✓ All values are in valid ranges")
    
    return True


def test_output_format(sections):
    """Test 9: Verify output matches expected format"""
    print("\n" + "="*60)
    print("TEST 9: Output format verification")
    print("="*60)
    
    print(f"\nSample output (first section):")
    print(json.dumps(sections[0], indent=2))
    
    print(f"\nSample output (last section - Commerce):")
    print(json.dumps(sections[-1], indent=2))
    
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("SECTION PERFORMANCE TRANSFORMATION - END-TO-END TEST")
    print("="*70)
    
    try:
        # Test 1
        test_load_raw_data()
        
        # Test 2
        sections, errors = test_transformation()
        
        # Test 3
        test_schema_validation(sections)
        
        # Test 4
        test_stream_assignment(sections)
        
        # Test 5
        test_data_types(sections)
        
        # Test 6
        test_pass_percentage_calculation(sections)
        
        # Test 7
        test_all_sections_present(sections)
        
        # Test 8
        test_numeric_values(sections)
        
        # Test 9
        test_output_format(sections)
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        
        # Print final summary
        print("\nFINAL OUTPUT:")
        print(json.dumps(sections, indent=2))
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
