#!/usr/bin/env python3
"""
Analyze threshold effectiveness for flare vs direct light separation.
"""

import numpy as np
import matplotlib.pyplot as plt
from flare_evaluation import FlareEvaluator
import sys


def analyze_data_distribution(data):
    """Analyze the intensity distribution of sensor data."""
    print("=== DATA DISTRIBUTION ANALYSIS ===")
    print(f"Data shape: {data.shape}")
    print(f"Min value: {np.min(data)}")
    print(f"Max value: {np.max(data)}")
    print(f"Mean: {np.mean(data):.2f}")
    print(f"Std dev: {np.std(data):.2f}")
    print(f"Median: {np.median(data):.2f}")
    
    # Percentile analysis
    percentiles = [50, 75, 90, 95, 98, 99, 99.5, 99.9]
    print("\nPercentile analysis:")
    for p in percentiles:
        val = np.percentile(data, p)
        print(f"  {p:5.1f}%: {val:7.1f}")
    
    # Current threshold analysis
    current_thresholds = {
        'offset': 64,
        'signal_threshold': 10,
        'light_threshold': 250,
        'max_value': 1023
    }
    
    print(f"\n=== CURRENT THRESHOLD ANALYSIS ===")
    flare_min = current_thresholds['offset'] + current_thresholds['signal_threshold']
    flare_max = current_thresholds['light_threshold']
    light_min = current_thresholds['light_threshold']
    light_max = current_thresholds['max_value']
    
    background_pixels = np.sum(data <= flare_min)
    flare_pixels = np.sum((data > flare_min) & (data <= flare_max))
    light_pixels = np.sum(data > light_min)
    
    total_pixels = data.size
    
    print(f"Background pixels (≤{flare_min}): {background_pixels:6d} ({100*background_pixels/total_pixels:5.2f}%)")
    print(f"Flare pixels ({flare_min}-{flare_max}):     {flare_pixels:6d} ({100*flare_pixels/total_pixels:5.2f}%)")
    print(f"Light pixels (>{light_min}):        {light_pixels:6d} ({100*light_pixels/total_pixels:5.2f}%)")
    
    # Intensity distribution in different ranges
    print(f"\n=== INTENSITY ANALYSIS IN RANGES ===")
    if flare_pixels > 0:
        flare_data = data[(data > flare_min) & (data <= flare_max)]
        print(f"Flare range ({flare_min}-{flare_max}):")
        print(f"  Mean: {np.mean(flare_data):.1f}")
        print(f"  75th percentile: {np.percentile(flare_data, 75):.1f}")
        print(f"  90th percentile: {np.percentile(flare_data, 90):.1f}")
        print(f"  95th percentile: {np.percentile(flare_data, 95):.1f}")
    
    if light_pixels > 0:
        light_data = data[data > light_min]
        print(f"Light range (>{light_min}):")
        print(f"  Mean: {np.mean(light_data):.1f}")
        print(f"  Min: {np.min(light_data):.1f}")
        print(f"  Max: {np.max(light_data):.1f}")


def suggest_improved_thresholds(data):
    """Suggest improved threshold values based on data distribution."""
    print(f"\n=== IMPROVED THRESHOLD SUGGESTIONS ===")
    
    # Use percentile-based approach
    p99_9 = np.percentile(data, 99.9)  # Very bright pixels (likely light sources)
    p99 = np.percentile(data, 99)      # Bright pixels
    p95 = np.percentile(data, 95)      # Moderately bright
    p90 = np.percentile(data, 90)      # Upper range
    
    # Suggested new thresholds
    suggested_light_threshold = max(p99, 600)  # Much higher than current 250
    suggested_direct_illum_threshold = max(p95, 400)  # New intermediate category
    
    print(f"Current light_threshold: 250")
    print(f"Suggested light_threshold: {suggested_light_threshold:.0f} (99th percentile or 600)")
    print(f"Suggested direct_illumination_threshold: {suggested_direct_illum_threshold:.0f} (95th percentile or 400)")
    
    # Calculate what this would change
    current_light = np.sum(data > 250)
    new_light = np.sum(data > suggested_light_threshold)
    direct_illum = np.sum((data > suggested_direct_illum_threshold) & (data <= suggested_light_threshold))
    
    print(f"\nClassification changes:")
    print(f"  Current light pixels (>250): {current_light}")
    print(f"  New light pixels (>{suggested_light_threshold:.0f}): {new_light}")
    print(f"  Direct illumination pixels ({suggested_direct_illum_threshold:.0f}-{suggested_light_threshold:.0f}): {direct_illum}")
    print(f"  Pixels reclassified from light to direct_illum: {current_light - new_light}")
    
    return {
        'light_threshold': suggested_light_threshold,
        'direct_illumination_threshold': suggested_direct_illum_threshold,
        'offset': 64,
        'signal_threshold': 10,
        'max_value': 1023
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_thresholds.py <data.csv>")
        sys.exit(1)
    
    # Load data
    data_file = sys.argv[1]
    data = np.loadtxt(data_file, delimiter=',')
    
    print(f"Analyzing: {data_file}")
    print("="*50)
    
    analyze_data_distribution(data)
    improved_thresholds = suggest_improved_thresholds(data)
    
    return improved_thresholds


if __name__ == "__main__":
    main()