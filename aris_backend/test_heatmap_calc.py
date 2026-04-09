"""
MANUAL VERIFICATION - Test pass % calculations before API
This ensures the formula is CORRECT before any visual representation
(No Django import - pure calculation)
"""

def verify_calculations():
    """
    Manually verify pass % calculations
    
    Formula: pass_percentage = ((Distinction + First Class + Second Class + Pass Class) / Total) * 100
    """
    print("\n" + "="*80)
    print("PASS % CALCULATION VERIFICATION")
    print("="*80)
    
    # Manual test 1: PCMB A - MATHS (Perfect Section)
    print("\n🧪 TEST 1: PCMB A - MATHS (Perfect Section)")
    distinction_a_math = 22
    first_class_a_math = 19
    second_class_a_math = 6
    pass_class_a_math = 5
    fail_a_math = 0
    total_a_math = 52
    
    pass_count_a_math = distinction_a_math + first_class_a_math + second_class_a_math + pass_class_a_math
    pass_pct_a_math = (pass_count_a_math / total_a_math) * 100
    
    print(f"   Distinction:  {distinction_a_math}")
    print(f"   First Class:  {first_class_a_math}")
    print(f"   Second Class: {second_class_a_math}")
    print(f"   Pass Class:   {pass_class_a_math}")
    print(f"   Fail:         {fail_a_math}")
    print(f"   Total:        {total_a_math}")
    print(f"   ---")
    print(f"   Pass Count: {pass_count_a_math}")
    print(f"   Pass %:     {pass_pct_a_math:.2f}%")
    print(f"   Expected:   100.00%")
    
    assert pass_pct_a_math == 100.0, f"FAIL: Expected 100%, got {pass_pct_a_math}%"
    print(f"   ✅ PASS")
    
    # Manual test 2: Subject with Fails (should use Fail count, but Fail NOT in pass calc)
    print("\n🧪 TEST 2: Subject with Fails (Fail NOT included in Pass %)")
    distinction_fail = 5
    first_class_fail = 8
    second_class_fail = 12
    pass_class_fail = 10
    fail_count = 17
    total_fail = 52
    
    pass_count_fail = distinction_fail + first_class_fail + second_class_fail + pass_class_fail
    pass_pct_fail = (pass_count_fail / total_fail) * 100
    
    print(f"   Distinction:  {distinction_fail}")
    print(f"   First Class:  {first_class_fail}")
    print(f"   Second Class: {second_class_fail}")
    print(f"   Pass Class:   {pass_class_fail}")
    print(f"   Fail:         {fail_count}  (⚠️  NOT included in pass count)")
    print(f"   Total:        {total_fail}")
    print(f"   ---")
    print(f"   Pass Count: {pass_count_fail} (NOT 52, because 17 failed)")
    print(f"   Pass %:     {pass_pct_fail:.2f}%")
    print(f"   Expected:   67.31%")
    
    expected_fail_pct = 67.31
    assert abs(pass_pct_fail - expected_fail_pct) < 0.1, f"FAIL: Expected ~67.31%, got {pass_pct_fail}%"
    print(f"   ✅ PASS")
    
    # Manual test 3: Edge case - All passes
    print("\n🧪 TEST 3: Edge Case - All Passes (100%)")
    pass_count_100 = 50
    total_100 = 50
    pass_pct_100 = (pass_count_100 / total_100) * 100
    print(f"   Pass Count: {pass_count_100} / {total_100}")
    print(f"   Pass %:     {pass_pct_100:.2f}%")
    assert pass_pct_100 == 100.0, f"FAIL: Expected 100%, got {pass_pct_100}%"
    print(f"   ✅ PASS")
    
    # Manual test 4: Edge case - All fails
    print("\n🧪 TEST 4: Edge Case - All Fails (0%)")
    pass_count_0 = 0
    total_0 = 50
    pass_pct_0 = (pass_count_0 / total_0) * 100
    print(f"   Pass Count: {pass_count_0} / {total_0}")
    print(f"   Pass %:     {pass_pct_0:.2f}%")
    assert pass_pct_0 == 0.0, f"FAIL: Expected 0%, got {pass_pct_0}%"
    print(f"   ✅ PASS")
    
    # Manual test 5: Decimal precision
    print("\n🧪 TEST 5: Decimal Precision")
    pass_count_decimal = 35
    total_decimal = 52
    pass_pct_decimal = (pass_count_decimal / total_decimal) * 100
    print(f"   Pass Count: {pass_count_decimal} / {total_decimal}")
    print(f"   Pass %:     {pass_pct_decimal:.2f}%")
    print(f"   Expected:   67.31%")
    expected_decimal = 67.31
    assert abs(pass_pct_decimal - expected_decimal) < 0.01, f"FAIL: Expected 67.31%, got {pass_pct_decimal}%"
    print(f"   ✅ PASS")
    
    print("\n" + "="*80)
    print("✅ ALL CALCULATIONS VERIFIED - SAFE TO VISUALIZE")
    print("="*80 + "\n")


if __name__ == "__main__":
    verify_calculations()
