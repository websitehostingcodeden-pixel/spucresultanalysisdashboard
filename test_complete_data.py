#!/usr/bin/env python
"""Test complete data transformer"""
import os
import sys

# Add the backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'aris_backend')
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()

from apps.results.services.heatmap_complete_data import get_science_complete_data, get_commerce_complete_data
from apps.results.services.heatmap_transformer import HeatmapTransformer

print("\n=== TESTING SCIENCE DATA ===")
df_science = get_science_complete_data()
print(f"✓ DataFrame shape: {df_science.shape}")

t_science = HeatmapTransformer(df_science)
records_science, errors_science = t_science.transform()

if errors_science:
    print(f"⚠ Errors: {errors_science[:3]}")

pcmb_a = [r for r in records_science if r['section'] == 'PCMB A']
print(f"✓ PCMB A subjects: {len(pcmb_a)}")
if pcmb_a:
    print(f"✓ Subjects: {sorted([r['subject'] for r in pcmb_a])}")

pcmb_b = [r for r in records_science if r['section'] == 'PCMB B']
print(f"✓ PCMB B subjects: {len(pcmb_b)}")

print(f"✓ Total Science records: {len(records_science)}")

print("\n=== TESTING COMMERCE DATA ===")
df_commerce = get_commerce_complete_data()
print(f"✓ DataFrame shape: {df_commerce.shape}")

t_commerce = HeatmapTransformer(df_commerce)
records_commerce, errors_commerce = t_commerce.transform()

if errors_commerce:
    print(f"⚠ Errors: {errors_commerce[:3]}")

ceba_g1 = [r for r in records_commerce if r['section'] == 'CEBA G1']
print(f"✓ CEBA G1 subjects: {len(ceba_g1)}")
if ceba_g1:
    print(f"✓ Subjects: {sorted([r['subject'] for r in ceba_g1])}")

print(f"✓ Total Commerce records: {len(records_commerce)}")
