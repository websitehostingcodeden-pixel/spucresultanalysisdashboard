"""
Simple end-to-end API test for section data transformation endpoints.
No Unicode characters to avoid encoding issues.
"""

import json
import sys
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

from django.test import Client


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
    print(f"Response status: {data.get('status')}")
    assert data['status'] == 'success'
    
    stats = data['sample']['statistics']
    print(f"Total sections: {stats['total_sections']}")
    print(f"Science sections: {stats['science_sections']}")
    print(f"Commerce sections: {stats['commerce_sections']}")
    print(f"Validation passed: {stats['validation_passed']}")
    
    assert stats['total_sections'] == 12
    assert stats['validation_passed'] == True
    
    transformed = data['transformed_data']
    print(f"Sections in response: {len(transformed)}")
    
    return transformed


def test_schema(sections):
    """Test schema validation"""
    print("\n" + "="*70)
    print("TEST 2: Schema validation")
    print("="*70)
    
    required_fields = {
        "section", "stream", "enrolled", "absent", "appeared",
        "distinction", "first_class", "second_class", "pass_class",
        "detained", "promoted", "pass_percentage"
    }
    
    errors = 0
    for section in sections:
        missing = required_fields - set(section.keys())
        if missing:
            print(f"ERROR: Section {section.get('section')} missing {missing}")
            errors += 1
    
    assert errors == 0, f"Found {errors} schema errors"
    print(f"OK: All {len(sections)} sections have required fields")


def test_streams(sections):
    """Test stream assignment"""
    print("\n" + "="*70)
    print("TEST 3: Stream assignment")
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
            assert stream == "Science"
            science_count += 1
        elif section_name in commerce_sections:
            assert stream == "Commerce"
            commerce_count += 1
    
    print(f"Science sections: {science_count}")
    print(f"Commerce sections: {commerce_count}")
    assert science_count == 6
    assert commerce_count == 6
    print("OK: Stream assignment correct")


def test_all_sections(sections):
    """Test all 12 sections present"""
    print("\n" + "="*70)
    print("TEST 4: All 12 sections present")
    print("="*70)
    
    expected = {
        "PCMB A", "PCMB B", "PCMB C", "PCMB D", "PCMC F", "PCME E",
        "CEBA G1", "CEBA G2", "CEBA/CSBA G3", "SEBA G4", "PEBA G6", "MSBA/MEBA G5"
    }
    
    found = {s["section"] for s in sections}
    
    missing = expected - found
    if missing:
        print(f"ERROR: Missing sections: {missing}")
        assert False
    
    extra = found - expected
    if extra:
        print(f"ERROR: Extra sections (totals?): {extra}")
        assert False
    
    print(f"OK: All 12 sections present")


def test_data_types(sections):
    """Test data types"""
    print("\n" + "="*70)
    print("TEST 5: Data type validation")
    print("="*70)
    
    errors = 0
    
    for section in sections:
        # Check counts are integers
        for key in ["enrolled", "absent", "appeared", "distinction",
                    "first_class", "second_class", "pass_class", "detained", "promoted"]:
            if not isinstance(section[key], int):
                print(f"ERROR: {section['section']} {key} is {type(section[key])}, expected int")
                errors += 1
        
        # Check percentage is float
        if not isinstance(section["pass_percentage"], float):
            print(f"ERROR: {section['section']} pass_percentage is {type(section['pass_percentage'])}, expected float")
            errors += 1
    
    assert errors == 0, f"Found {errors} type errors"
    print("OK: All data types correct")


def test_percentages(sections):
    """Test pass percentage calculation"""
    print("\n" + "="*70)
    print("TEST 6: Pass percentage validation")
    print("="*70)
    
    errors = 0
    
    for section in sections:
        appeared = section["appeared"]
        if appeared == 0:
            continue
        
        passed = (
            section["distinction"] + section["first_class"] +
            section["second_class"] + section["pass_class"]
        )
        
        expected = round((passed / appeared) * 100, 2)
        actual = section["pass_percentage"]
        
        if abs(expected - actual) > 0.01:
            print(f"ERROR: {section['section']} expected {expected}%, got {actual}%")
            errors += 1
        
        # Check percentage is 0-100
        if actual < 0 or actual > 100:
            print(f"ERROR: {section['section']} pass_percentage out of range: {actual}")
            errors += 1
    
    assert errors == 0, f"Found {errors} percentage errors"
    print("OK: All pass percentages valid")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*75)
    print("SECTION PERFORMANCE API - END-TO-END TEST")
    print("="*75)
    
    try:
        sections = test_sample_endpoint()
        test_schema(sections)
        test_streams(sections)
        test_all_sections(sections)
        test_data_types(sections)
        test_percentages(sections)
        
        print("\n" + "="*75)
        print("SUCCESS: ALL TESTS PASSED")
        print("="*75)
        
        # Print sample output
        print("\nSample Output - First 3 sections (JSON):")
        print(json.dumps(sections[:3], indent=2))
        
        print("\n\nSample Output - Last 3 sections (JSON):")
        print(json.dumps(sections[-3:], indent=2))
        
        # Overall stats
        print("\n\nOverall Statistics:")
        print(f"Total sections transformed: {len(sections)}")
        print(f"Science sections: {len([s for s in sections if s['stream'] == 'Science'])}")
        print(f"Commerce sections: {len([s for s in sections if s['stream'] == 'Commerce'])}")
        
        min_pass = min(s['pass_percentage'] for s in sections)
        max_pass = max(s['pass_percentage'] for s in sections)
        avg_pass = sum(s['pass_percentage'] for s in sections) / len(sections)
        
        print(f"Pass percentage range: {min_pass}% to {max_pass}%")
        print(f"Average pass percentage: {avg_pass:.2f}%")
        
        return True
        
    except AssertionError as e:
        print(f"\nFAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
