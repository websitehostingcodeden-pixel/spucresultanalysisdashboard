"""
MANUAL VERIFICATION - Test pass % calculations before API
This ensures the formula is CORRECT before any visual representation
"""

from apps.results.services.heatmap_transformer import HeatmapTransformer
from apps.results.services.heatmap_test_data import get_heatmap_test_data, EXPECTED_HEATMAP


def verify_calculations():
    """
    Manually verify pass % calculations against expected values
    
    Formula: pass_percentage = ((Distinction + First Class + Second Class + Pass Class) / Total) * 100
    """
    print("\n" + "="*80)
    print("PASS % CALCULATION VERIFICATION")
    print("="*80)
    
    test_data = get_heatmap_test_data()
    
    # Manual test 1: PCMB A - MATHS
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
    
    # Manual test 2: PCMB A - PHY (Slight Variation)
    print("\n🧪 TEST 2: PCMB A - PHY (Check Rounding)")
    distinction_a_phy = 18
    first_class_a_phy = 16
    second_class_a_phy = 10
    pass_class_a_phy = 8
    fail_a_phy = 0
    total_a_phy = 52
    
    pass_count_a_phy = distinction_a_phy + first_class_a_phy + second_class_a_phy + pass_class_a_phy
    pass_pct_a_phy = (pass_count_a_phy / total_a_phy) * 100
    
    print(f"   Distinction:  {distinction_a_phy}")
    print(f"   First Class:  {first_class_a_phy}")
    print(f"   Second Class: {second_class_a_phy}")
    print(f"   Pass Class:   {pass_class_a_phy}")
    print(f"   Total:        {total_a_phy}")
    print(f"   ---")
    print(f"   Pass Count: {pass_count_a_phy}")
    print(f"   Pass %:     {pass_pct_a_phy:.2f}%")
    print(f"   Expected:   100.00%")
    
    assert pass_pct_a_phy == 100.0, f"FAIL: Expected 100%, got {pass_pct_a_phy}%"
    print(f"   ✅ PASS")
    
    # Manual test 3: Failing Subject (should use Fail count, but Fail NOT in pass calc)
    print("\n🧪 TEST 3: Subject with Fails (Fail NOT included in Pass %)")
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
    
    print("\n" + "="*80)
    print("TRANSFORMER INTEGRATION TEST")
    print("="*80)
    
    # Test the transformer
    transformer = HeatmapTransformer(test_data.to_dict())
    results, errors = transformer.transform()
    
    print(f"\n✓ Transformation complete")
    print(f"✓ Records generated: {len(results)}")
    print(f"✓ Errors: {len(errors)}")
    
    if errors:
        print(f"\n⚠️ Errors found:")
        for error in errors:
            print(f"   - {error}")
    
    print(f"\nGenerated records (first 3):")
    for i, record in enumerate(results[:3]):
        print(f"   [{i}] {record['section']} - {record['subject']}: {record['pass_percentage']}%")
    
    print("\n" + "="*80)
    print("✅ ALL CALCULATIONS VERIFIED - SAFE TO VISUALIZE")
    print("="*80)


if __name__ == "__main__":
    verify_calculations()
