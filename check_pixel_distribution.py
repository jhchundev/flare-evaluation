#!/usr/bin/env python3
"""
Check pixel distribution in specific ranges for the Gemini image.
"""

import numpy as np

# Load the data
data = np.loadtxt('data/gemini_flare_10bit.csv', delimiter=',')

print("=== PIXEL DISTRIBUTION ANALYSIS ===")
print(f"Total pixels: {data.size}")

# Check various ranges
ranges = [
    (250, 400, "Old light -> New direct illumination"),
    (400, 600, "New direct illumination -> New light"),
    (600, 1023, "New light source cores"),
    (74, 250, "Old flare range"),
    (74, 400, "New flare range")
]

for min_val, max_val, description in ranges:
    pixels_in_range = np.sum((data > min_val) & (data <= max_val))
    percentage = (pixels_in_range / data.size) * 100
    print(f"{description:35s}: {pixels_in_range:6d} pixels ({percentage:5.2f}%)")
    
    if pixels_in_range > 0:
        range_data = data[(data > min_val) & (data <= max_val)]
        print(f"  Range: {np.min(range_data):.0f} - {np.max(range_data):.0f}, Mean: {np.mean(range_data):.1f}")

print(f"\n=== THRESHOLD ANALYSIS ===")
print("Current thresholds:")
print("  light_threshold: 600 (new)")
print("  direct_illumination_threshold: 400 (new)")
print("  Old light_threshold: 250")

# Compare classifications
old_light = np.sum(data > 250)
new_light = np.sum(data > 600) 
direct_illum = np.sum((data > 400) & (data <= 600))
reclassified = np.sum((data > 250) & (data <= 400))

print(f"\nClassification changes:")
print(f"  Old light pixels (>250): {old_light}")
print(f"  New light pixels (>600): {new_light}")
print(f"  Direct illumination (400-600): {direct_illum}")
print(f"  Reclassified pixels (250-400): {reclassified}")

# Check if we need to adjust thresholds
if direct_illum == 0 and reclassified > 0:
    print(f"\n=== THRESHOLD ADJUSTMENT SUGGESTION ===")
    print("No pixels in direct illumination range (400-600)")
    print(f"But {reclassified} pixels in range 250-400 could be direct illumination")
    print("Consider lowering direct_illumination_threshold to ~300")
    
    suggested_direct_illum = 300
    new_direct_illum = np.sum((data > suggested_direct_illum) & (data <= 600))
    new_reclassified = np.sum((data > 250) & (data <= suggested_direct_illum))
    
    print(f"With direct_illumination_threshold = {suggested_direct_illum}:")
    print(f"  Direct illumination pixels: {new_direct_illum}")
    print(f"  Remaining reclassified: {new_reclassified}")