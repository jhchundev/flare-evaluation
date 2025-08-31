#!/usr/bin/env python3
"""
Debug the evaluation results to see why direct illumination is showing as 0.
"""

import numpy as np
from flare_evaluation import FlareEvaluator

# Load data
data = np.loadtxt('data/gemini_flare_10bit.csv', delimiter=',')
print(f"Data loaded: {data.shape}")

# Create evaluator with default (new) config
evaluator = FlareEvaluator()
print("Default config:", evaluator.config)

# Perform evaluation
results = evaluator.evaluate(data)

print("\n=== EVALUATION RESULTS ===")
for key, value in results.items():
    if isinstance(value, np.ndarray):
        print(f"{key}: array shape {value.shape}, dtype {value.dtype}")
        if key.endswith('_mask'):
            print(f"  Non-zero pixels: {np.sum(value > 0)}")
    else:
        print(f"{key}: {value}")

print("\n=== MANUAL THRESHOLD CHECK ===")
offset = evaluator.config['offset']
signal_threshold = evaluator.config['signal_threshold']
direct_illumination_threshold = evaluator.config['direct_illumination_threshold']
light_threshold = evaluator.config['light_threshold']

print(f"offset: {offset}")
print(f"signal_threshold: {signal_threshold}")
print(f"direct_illumination_threshold: {direct_illumination_threshold}")
print(f"light_threshold: {light_threshold}")

# Manual calculations
flare_pixels = np.sum((data > offset + signal_threshold) & (data <= direct_illumination_threshold))
direct_illum_pixels = np.sum((data > direct_illumination_threshold) & (data <= light_threshold))
light_pixels = np.sum(data > light_threshold)

print(f"\nManual calculations:")
print(f"Flare pixels (>{offset + signal_threshold} & <={direct_illumination_threshold}): {flare_pixels}")
print(f"Direct illum pixels (>{direct_illumination_threshold} & <={light_threshold}): {direct_illum_pixels}")
print(f"Light pixels (>{light_threshold}): {light_pixels}")

# Check if results match
print(f"\nComparison:")
print(f"Flare - Algorithm: {results['signal_pixel_count']}, Manual: {flare_pixels}")
print(f"Direct - Algorithm: {results.get('direct_illumination_pixel_count', 'MISSING')}, Manual: {direct_illum_pixels}")
print(f"Light - Algorithm: {results['light_pixel_count']}, Manual: {light_pixels}")