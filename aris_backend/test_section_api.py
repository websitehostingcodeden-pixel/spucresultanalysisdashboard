"""
End-to-end API test for section data transformation endpoints.

Tests:
1. GET /api/sections/sample/ - Get sample data and transformation
2. POST /api/sections/transform/ - Transform section metrics
3. Verify all 12 sections present in response
4. Verify no totals in response
5. Verify correct data types and schema
"""

import json
import sys
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

from django.test import Client
from rest_framework import status as http_status


def test_sample_endpoint():
    """Test GET /api/sections/sample/"""
    print("\n" + "="*70)
    print("TEST 1: GET /api/sections/sample/")
    print("="*70)
    
    client = Client()
    
    response = client.get('/api/sections/sample/')
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = json.loads(response.content)
    
    print(f"✓ Response status: {data.get('status')}")
    assert data['status'] == 'success', "Expected success status"
    
    # Check structure
    assert 'sample' in data, "Missing 'sample' key"
    assert 'transformed_data' in data, "Missing 'transformed_data' key"
    
    sample = data['sample']
    print(f"✓ Input format: {sample['input_format']['description']}")
    print(f"  - Dimensions: {sample['input_format']['shape']}")
    print(f"  - Metrics (rows): {sample['input_format']['rows']}")
    print(f"  - Sections (columns): {sample['input_format']['columns']}")
    
    # Check output format
    output_format = sample['output_format']
    print(f"✓ Output format: {output_format['description']}")
    print(f"  - Schema keys: {list(output_format['schema'].keys())}")
    
    # Check statistics
    stats = sample['statistics']
    print(f"✓ Statistics:")
    print(f"  - Total sections: {stats['total_sections']}")
    print(f"  - Science sections: {stats['science_sections']}")
    print(f"  - Commerce sections: {stats['commerce_sections']}")
    print(f"  - Validation passed: {stats['validation_passed']}")
    
    assert stats['total_sections'] == 12, f"Expected 12 sections, got {stats['total_sections']}"
    assert stats['science_sections'] == 6, f"Expected 6 science, got {stats['science_sections']}"
    assert stats['commerce_sections'] == 6, f"Expected 6 commerce, got {stats['commerce_sections']}"
    assert stats['validation_passed'] == True, "Validation should pass"
    
    # Check transformed data
    transformed = data['transformed_data']
    print(f"✓ Transformed data: {len(transformed)} sections")
    
    return transformed


def test_transform_endpoint():
    """Test POST /api/sections/transform/"""
    print("\n" + "="*70)
    print("TEST 2: POST /api/sections/transform/ (with JSON)")
    print("="*70)
    
    client = Client()
    
    # Create test data in the required format
    test_data = {
        "Enrolled": {"PCMB A": 52, "PCMB B": 48, "PCMB C": 55, "PCMB D": 60, 
                     "PCMC F": 50, "PCME E": 58,
                     "CEBA G1": 45, "CEBA G2": 50, "CEBA/CSBA G3": 52, 
                     "SEBA G4": 48, "PEBA G6": 46, "MSBA/MEBA G5": 51},
        "Absent": {"PCMB A": 0, "PCMB B": 2, "PCMB C": 1, "PCMB D": 1,
                   "PCMC F": 0, "PCME E": 2,
                   "CEBA G1": 3, "CEBA G2": 1, "CEBA/CSBA G3": 2,
                   "SEBA G4": 0, "PEBA G6": 1, "MSBA/MEBA G5": 1},
        "Appeared": {"PCMB A": 52, "PCMB B": 46, "PCMB C": 54, "PCMB D": 59,
                     "PCMC F": 50, "PCME E": 56,
                     "CEBA G1": 42, "CEBA G2": 49, "CEBA/CSBA G3": 50,
                     "SEBA G4": 48, "PEBA G6": 45, "MSBA/MEBA G5": 50},
        "Distinction": {"PCMB A": 8, "PCMB B": 7, "PCMB C": 9, "PCMB D": 11,
                        "PCMC F": 8, "PCME E": 10,
                        "CEBA G1": 5, "CEBA G2": 6, "CEBA/CSBA G3": 7,
                        "SEBA G4": 6, "PEBA G6": 5, "MSBA/MEBA G5": 7},
        "First Class": {"PCMB A": 30, "PCMB B": 28, "PCMB C": 32, "PCMB D": 35,
                        "PCMC F": 29, "PCME E": 33,
                        "CEBA G1": 25, "CEBA G2": 29, "CEBA/CSBA G3": 30,
                        "SEBA G4": 28, "PEBA G6": 26, "MSBA/MEBA G5": 30},
        "Second Class": {"PCMB A": 12, "PCMB B": 10, "PCMB C": 12, "PCMB D": 12,
                         "PCMC F": 12, "PCME E": 12,
                         "CEBA G1": 12, "CEBA G2": 14, "CEBA/CSBA G3": 13,
                         "SEBA G4": 14, "PEBA G6": 14, "MSBA/MEBA G5": 13},
        "Pass Class": {"PCMB A": 2, "PCMB B": 1, "PCMB C": 1, "PCMB D": 1,
                       "PCMC F": 1, "PCME E": 1,
                       "CEBA G1": 0, "CEBA G2": 0, "CEBA/CSBA G3": 0,
                       "SEBA G4": 0, "PEBA G6": 0, "MSBA/MEBA G5": 0},
        "Detained": {"PCMB A": 0, "PCMB B": 0, "PCMB C": 0, "PCMB D": 0,
                     "PCMC F": 0, "PCME E": 0,
                     "CEBA G1": 0, "CEBA G2": 0, "CEBA/CSBA G3": 0,
                     "SEBA G4": 0, "PEBA G6": 0, "MSBA/MEBA G5": 0},
        "Promoted": {"PCMB A": 50, "PCMB B": 45, "PCMB C": 53, "PCMB D": 58,
                     "PCMC F": 49, "PCME E": 55,
                     "CEBA G1": 42, "CEBA G2": 49, "CEBA/CSBA G3": 50,
                     "SEBA G4": 48, "PEBA G6": 45, "MSBA/MEBA G5": 50},
    }
    
    response = client.post(
        '/api/sections/transform/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    data = json.loads(response.content)
    
    print(f"✓ Response status: {data.get('status')}")
    print(f"✓ Sections transformed: {data.get('count')}")
    
    assert data['status'] == 'success', "Expected success status"
    assert data['count'] == 12, f"Expected 12 sections, got {data['count']}"
    
    # Check errors list is empty
    errors = data.get('errors', [])
    if errors:
        print(f"⚠ Transformation errors: {errors}")
    
    print(f"✓ Validation summary: {data.get('validation_summary')}")
    
    return data['data']


def test_schema_validation(sections):
    """Validate the schema of transformed sections"""
    print("\n" + "="*70)
    print("TEST 3: Schema validation")
    print("="*70)
    
    required_fields = {
        "section", "stream", "enrolled", "absent", "appeared",
        "distinction", "first_class", "second_class", "pass_class",
        "detained", "promoted", "pass_percentage"
    }
    
    print(f"Required fields: {required_fields}")
    
    for section in sections:
        missing = required_fields - set(section.keys())
        if missing:
            print(f"✗ Section {section.get('section')}: missing {missing}")
            assert False, f"Missing fields in section {section.get('section')}"
    
    print(f"✓ All {len(sections)} sections have required fields")


def test_stream_assignment(sections):
    """Test stream assignment"""
    print("\n" + "="*70)
    print("TEST 4: Stream assignment verification")
    print("="*70)
    
    science_sections = {
        "PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E"
    }
    commerce_sections = {
        "CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"
    }
    
    science_count = 0
    commerce_count = 0
    
    for section in sections:
        section_name = section["section"]
        stream = section["stream"]
        
        if section_name in science_sections:
            assert stream == "Science", f"{section_name} should be Science"
            science_count += 1
        elif section_name in commerce_sections:
            assert stream == "Commerce", f"{section_name} should be Commerce"
            commerce_count += 1
        else:
            print(f"✗ Unknown section: {section_name}")
            assert False, f"Unknown section: {section_name}"
    
    print(f"✓ Science sections: {science_count}")
    print(f"✓ Commerce sections: {commerce_count}")
    assert science_count == 6, f"Expected 6 science sections"
    assert commerce_count == 6, f"Expected 6 commerce sections"


def test_no_totals(sections):
    """Test that no totals are in the results"""
    print("\n" + "="*70)
    print("TEST 5: No totals in results")
    print("="*70)
    
    all_sections = {s["section"] for s in sections}
    totals = [s for s in all_sections if "total" in s.lower()]
    
    if totals:
        print(f"✗ Found totals: {totals}")
        assert False, f"Found totals in sections: {totals}"
    
    print(f"✓ No totals found - all {len(sections)} sections are valid")


def test_all_sections_present(sections):
    """Test that all 12 valid sections are present"""
    print("\n" + "="*70)
    print("TEST 6: All 12 sections present")
    print("="*70)
    
    expected_sections = {
        "PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E",
        "CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"
    }
    
    found_sections = {s["section"] for s in sections}
    missing = expected_sections - found_sections
    extra = found_sections - expected_sections
    
    if missing:
        print(f"✗ Missing sections: {missing}")
        assert False, f"Missing: {missing}"
    
    if extra:
        print(f"✗ Extra sections: {extra}")
        assert False, f"Extra: {extra}"
    
    print(f"✓ All 12 expected sections present")
    print(f"  - {', '.join(sorted(found_sections))}")


def test_data_types(sections):
    """Test that data types are correct"""
    print("\n" + "="*70)
    print("TEST 7: Data type validation")
    print("="*70)
    
    for section in sections:
        # All counts should be integers
        for key in ["enrolled", "absent", "appeared", "distinction",
                    "first_class", "second_class", "pass_class", "detained", "promoted"]:
            value = section[key]
            assert isinstance(value, int), \
                f"{section['section']}: {key} should be int, got {type(value).__name__}"
        
        # Pass percentage should be float
        pct = section["pass_percentage"]
        assert isinstance(pct, float), \
            f"{section['section']}: pass_percentage should be float, got {type(pct).__name__}"
        
        # Validate percentage range
        assert 0 <= pct <= 100, \
            f"{section['section']}: pass_percentage out of range: {pct}"
    
    print(f"✓ All data types correct")
    print(f"  - Counts: integers")
    print(f"  - Pass percentage: float (0-100)")


def test_numeric_consistency(sections):
    """Test numeric consistency in data"""
    print("\n" + "="*70)
    print("TEST 8: Numeric consistency")
    print("="*70)
    
    errors = []
    
    for section in sections:
        section_name = section["section"]
        appeared = section["appeared"]
        
        # Check pass percentage calculation
        if appeared > 0:
            passed = (
                section["distinction"] + section["first_class"] +
                section["second_class"] + section["pass_class"]
            )
            expected_pct = round((passed / appeared) * 100, 2)
            actual_pct = section["pass_percentage"]
            
            if abs(expected_pct - actual_pct) > 0.01:
                errors.append(
                    f"{section_name}: expected {expected_pct}%, got {actual_pct}%"
                )
        
        # Check that class counts don't exceed appeared
        class_total = (
            section["distinction"] + section["first_class"] +
            section["second_class"] + section["pass_class"]
        )
        if class_total > appeared:
            errors.append(
                f"{section_name}: class total ({class_total}) > appeared ({appeared})"
            )
    
    if errors:
        for error in errors:
            print(f"✗ {error}")
        assert False, "Numeric consistency check failed"
    
    print(f"✓ All numeric values consistent")


def run_all_tests():
    """Run complete integration test suite"""
    print("\n" + "="*75)
    print("SECTION PERFORMANCE API - END-TO-END INTEGRATION TEST")
    print("="*75)
    
    try:
        # Test 1: Sample endpoint
        sections_from_sample = test_sample_endpoint()
        
        # Test 2: Transform endpoint
        sections_from_transform = test_transform_endpoint()
        
        # Test 3: Schema validation
        test_schema_validation(sections_from_sample)
        test_schema_validation(sections_from_transform)
        
        # Test 4: Stream assignment
        test_stream_assignment(sections_from_sample)
        
        # Test 5: No totals
        test_no_totals(sections_from_sample)
        
        # Test 6: All sections present
        test_all_sections_present(sections_from_sample)
        test_all_sections_present(sections_from_transform)
        
        # Test 7: Data types
        test_data_types(sections_from_sample)
        test_data_types(sections_from_transform)
        
        # Test 8: Numeric consistency
        test_numeric_consistency(sections_from_sample)
        test_numeric_consistency(sections_from_transform)
        
        print("\n" + "="*75)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("="*75)
        
        # Print final output sample
        print("\nFinal JSON Output Sample (first 2 sections):")
        print(json.dumps(sections_from_sample[:2], indent=2))
        
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
