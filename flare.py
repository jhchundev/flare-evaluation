#!/usr/bin/env python3
"""
Flare Evaluation System - Simple tool for analyzing lens flare
Usage: python flare.py
       (Edit config.py to change parameters)
"""

import numpy as np
import json
import sys
from pathlib import Path
from PIL import Image

# Import configuration
try:
    from config import CONFIG
except ImportError:
    print("Error: config.py not found. Creating default config...")
    CONFIG = {
        'mode': 'grayscale',
        'input_file': 'data/gemini_flare_10bit.csv',
        'pixel_pitch': 2.4,
        'offset': 64,
        'signal_threshold': 10,
        'direct_threshold': 200,
        'light_threshold': 250,
        'beta': 0.5
    }

def process_grayscale(filepath):
    """Process grayscale sensor data - evaluate and visualize."""
    print(f"\n📊 Processing grayscale data: {filepath}")
    
    # Load data
    try:
        data = np.loadtxt(filepath, delimiter=',')
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)
    
    # Get parameters from config
    pixel_pitch = CONFIG.get('pixel_pitch', 2.4)
    pixel_area = pixel_pitch ** 2
    offset = CONFIG.get('offset', 64)
    signal_threshold = CONFIG.get('signal_threshold', 10)
    direct_threshold = CONFIG.get('direct_threshold', 200)
    light_threshold = CONFIG.get('light_threshold', 250)
    beta = CONFIG.get('beta', 0.5)
    
    # Classify pixels
    flare_mask = (data > offset + signal_threshold) & (data <= direct_threshold)
    direct_mask = (data > direct_threshold) & (data <= light_threshold)
    light_mask = data > light_threshold
    
    # Calculate metrics
    N_sensor = data.size
    N_flare = np.sum(flare_mask)
    N_direct = np.sum(direct_mask)
    N_light = np.sum(light_mask)
    
    # F_raw calculation
    if N_flare > 0:
        flare_values = data[flare_mask] - offset
        F_raw = np.sum(flare_values) / (N_flare * pixel_area)
    else:
        F_raw = 0
    
    # F_norm calculation
    F_norm = 0
    if N_flare > 0 and N_direct > 0:
        flare_values = data[flare_mask] - offset
        direct_values = data[direct_mask] - offset
        flare_intensity = np.sum(flare_values) / (N_flare * pixel_area)
        direct_intensity = np.sum(direct_values) / (N_direct * pixel_area)
        if direct_intensity > 0:
            F_norm = flare_intensity / direct_intensity
    
    # F_final calculation
    coverage_ratio = N_flare / N_sensor if N_sensor > 0 else 0
    F_final = F_norm * (coverage_ratio ** beta)
    
    # Display results
    print("\n" + "="*60)
    print("FLARE EVALUATION RESULTS (Grayscale)")
    print("="*60)
    print(f"Sensor: {data.shape[0]}×{data.shape[1]} pixels")
    print(f"Pixel pitch: {pixel_pitch:.2f} µm")
    print(f"\n📊 Resolution-Independent Metrics:")
    print(f"  F_raw:   {F_raw:.4f} ADU/µm²")
    print(f"  F_norm:  {F_norm:.4f} (dimensionless)")
    print(f"  F_final: {F_final:.6f} (coverage-weighted)")
    print(f"\n📈 Detection Statistics:")
    print(f"  Flare pixels:  {N_flare:,} ({coverage_ratio*100:.2f}%)")
    print(f"  Direct pixels: {N_direct:,}")
    print(f"  Light pixels:  {N_light:,}")
    print("="*60)
    
    # Save JSON results
    results = {
        'mode': 'grayscale',
        'F_raw': F_raw,
        'F_norm': F_norm,
        'F_final': F_final,
        'pixel_pitch_um': pixel_pitch,
        'flare_pixels': int(N_flare),
        'direct_pixels': int(N_direct),
        'light_pixels': int(N_light),
        'flare_coverage_percent': coverage_ratio * 100
    }
    
    output_json = CONFIG.get('output_json', 'output/results.json')
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_json}")
    
    # Create visualization
    print(f"\n🎨 Creating visualization...")
    height, width = data.shape
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Base intensity (dark background)
    norm_data = (data - data.min()) / (data.max() - data.min() + 1e-10)
    base = (norm_data * 50).astype(np.uint8)
    img[:,:,0] = base
    img[:,:,1] = base
    img[:,:,2] = base
    
    # Color code regions
    img[flare_mask] = [255, 255, 0]      # Yellow for flare
    img[direct_mask] = [255, 165, 0]     # Orange for direct illumination
    img[light_mask] = [255, 0, 0]        # Red for light sources
    
    # Save image
    output_image = CONFIG.get('output_image', 'output/visualization.png')
    Path(output_image).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(output_image)
    print(f"✅ Visualization saved to: {output_image}")
    
    return results

def process_rgb(filepath):
    """Process RGB sensor data - evaluate and visualize."""
    print(f"\n📊 Processing RGB data: {filepath}")
    
    # Load RGB data
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)
    
    height = len(lines)
    width = len(lines[0].strip().split(','))
    
    r_data = np.zeros((height, width))
    g_data = np.zeros((height, width))
    b_data = np.zeros((height, width))
    
    # Parse RGB values (handles variable spacing)
    for row_idx, line in enumerate(lines):
        cells = line.strip().split(',')
        for col_idx, cell in enumerate(cells):
            rgb_values = cell.strip().split()
            if len(rgb_values) == 3:
                r_data[row_idx, col_idx] = float(rgb_values[0])
                g_data[row_idx, col_idx] = float(rgb_values[1])
                b_data[row_idx, col_idx] = float(rgb_values[2])
            elif len(rgb_values) == 1:
                # Handle single value as grayscale
                value = float(rgb_values[0])
                r_data[row_idx, col_idx] = value
                g_data[row_idx, col_idx] = value
                b_data[row_idx, col_idx] = value
    
    # Get parameters
    pixel_pitch = CONFIG.get('pixel_pitch', 2.4)
    pixel_area = pixel_pitch ** 2
    offset = CONFIG.get('offset', 64)
    signal_threshold = CONFIG.get('signal_threshold', 10)
    direct_threshold = CONFIG.get('direct_threshold', 200)
    light_threshold = CONFIG.get('light_threshold', 250)
    beta = CONFIG.get('beta', 0.5)
    
    print("\n" + "="*60)
    print("FLARE EVALUATION RESULTS (RGB)")
    print("="*60)
    print(f"Sensor: {height}×{width} pixels (RGB)")
    print(f"Pixel pitch: {pixel_pitch:.2f} µm")
    
    results = {'mode': 'rgb', 'channels': {}}
    
    # Process each channel
    for channel_name, data in [('R', r_data), ('G', g_data), ('B', b_data)]:
        # Classify pixels
        flare_mask = (data > offset + signal_threshold) & (data <= direct_threshold)
        direct_mask = (data > direct_threshold) & (data <= light_threshold)
        light_mask = data > light_threshold
        
        N_sensor = data.size
        N_flare = np.sum(flare_mask)
        N_direct = np.sum(direct_mask)
        
        # Calculate metrics
        if N_flare > 0:
            flare_values = data[flare_mask] - offset
            F_raw = np.sum(flare_values) / (N_flare * pixel_area)
        else:
            F_raw = 0
        
        F_norm = 0
        if N_flare > 0 and N_direct > 0:
            flare_values = data[flare_mask] - offset
            direct_values = data[direct_mask] - offset
            flare_intensity = np.sum(flare_values) / (N_flare * pixel_area)
            direct_intensity = np.sum(direct_values) / (N_direct * pixel_area)
            if direct_intensity > 0:
                F_norm = flare_intensity / direct_intensity
        
        coverage_ratio = N_flare / N_sensor if N_sensor > 0 else 0
        F_final = F_norm * (coverage_ratio ** beta)
        
        print(f"\n📊 {channel_name} Channel:")
        print(f"  F_raw:   {F_raw:.4f} ADU/µm²")
        print(f"  F_norm:  {F_norm:.4f}")
        print(f"  F_final: {F_final:.6f}")
        print(f"  Flare pixels: {N_flare:,} ({coverage_ratio*100:.2f}%)")
        
        results['channels'][channel_name] = {
            'F_raw': F_raw,
            'F_norm': F_norm,
            'F_final': F_final,
            'flare_pixels': int(N_flare),
            'coverage_percent': coverage_ratio * 100
        }
    
    # Calculate average metrics across channels
    avg_F_raw = np.mean([ch['F_raw'] for ch in results['channels'].values()])
    avg_F_norm = np.mean([ch['F_norm'] for ch in results['channels'].values()])
    avg_F_final = np.mean([ch['F_final'] for ch in results['channels'].values()])
    
    print(f"\n📊 Average Across Channels:")
    print(f"  F_raw:   {avg_F_raw:.4f} ADU/µm²")
    print(f"  F_norm:  {avg_F_norm:.4f}")
    print(f"  F_final: {avg_F_final:.6f}")
    
    results['average'] = {
        'F_raw': avg_F_raw,
        'F_norm': avg_F_norm,
        'F_final': avg_F_final
    }
    
    print("="*60)
    
    # Save JSON results
    output_json = CONFIG.get('output_json', 'output/results.json')
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_json}")
    
    # Create RGB visualization
    print(f"\n🎨 Creating RGB visualization...")
    
    # Use luminance for classification
    lum_data = 0.299 * r_data + 0.587 * g_data + 0.114 * b_data
    flare_mask = (lum_data > offset + signal_threshold) & (lum_data <= direct_threshold)
    direct_mask = (lum_data > direct_threshold) & (lum_data <= light_threshold)
    light_mask = lum_data > light_threshold
    
    # Create true-color RGB image with enhancements
    r_norm = np.clip((r_data / 1023) * 255, 0, 255).astype(np.uint8)
    g_norm = np.clip((g_data / 1023) * 255, 0, 255).astype(np.uint8)
    b_norm = np.clip((b_data / 1023) * 255, 0, 255).astype(np.uint8)
    
    img = np.stack([r_norm, g_norm, b_norm], axis=-1)
    
    # Enhance flare regions
    img[flare_mask, 0] = np.minimum(255, img[flare_mask, 0] * 1.2).astype(np.uint8)
    img[flare_mask, 1] = np.minimum(255, img[flare_mask, 1] * 1.2).astype(np.uint8)
    img[flare_mask, 2] = (img[flare_mask, 2] * 0.8).astype(np.uint8)
    
    # Mark light sources
    img[light_mask] = [255, 255, 255]
    
    # Save image
    output_image = CONFIG.get('output_image', 'output/visualization.png')
    Path(output_image).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(output_image)
    print(f"✅ RGB visualization saved to: {output_image}")
    
    return results

def show_help():
    """Display help information."""
    print("""
================================================================================
                        FLARE EVALUATION SYSTEM
================================================================================

Simple tool for evaluating lens flare in image sensors.
Supports both grayscale and RGB sensor data.

USAGE:
------
1. Edit config.py to set your parameters
2. Run: python flare.py

MODES (set in config.py):
-------------------------
'grayscale'  - Process single-value-per-cell CSV data
'rgb'        - Process RGB data (R G B per cell)

Both modes automatically:
- Calculate flare metrics (F_raw, F_norm, F_final)
- Save JSON results
- Create visualization image

KEY PARAMETERS (in config.py):
------------------------------
mode         - 'grayscale' or 'rgb'
input_file   - Input CSV file path
output_json  - Output JSON results path
output_image - Output visualization path
pixel_pitch  - Sensor pixel pitch in micrometers
offset       - Black level/offset in ADU
signal_threshold - Minimum signal above offset
direct_threshold - Direct illumination threshold
light_threshold  - Light source threshold

RESOLUTION-INDEPENDENT METRICS:
-------------------------------
F_raw   - Physical flare intensity (ADU/µm²)
F_norm  - Normalized flare ratio (dimensionless)
F_final - Coverage-weighted index (dimensionless)

DATA FORMATS:
------------
Grayscale: Single values per cell
  Example: 100.5,150.2,200.8

RGB: Three space-separated values per cell (R G B)
  Example: 100 100 100,150 145 140,200 195 185
  Supports variable spacing: 100   100   100

OUTPUT FILES:
------------
- JSON file with all metrics
- PNG visualization with color coding:
  * Yellow = Flare regions
  * Orange = Direct illumination
  * Red = Light sources
  * Dark = Background

================================================================================
""")

def main():
    """Main entry point."""
    mode = CONFIG.get('mode', 'grayscale')
    
    print(f"🔧 Flare System - Mode: {mode}")
    
    if mode == 'grayscale':
        input_file = CONFIG.get('input_file')
        if not input_file:
            print("❌ Error: input_file not specified in config.py")
            sys.exit(1)
        process_grayscale(input_file)
        
    elif mode == 'rgb':
        input_file = CONFIG.get('input_file')
        if not input_file:
            print("❌ Error: input_file not specified in config.py")
            sys.exit(1)
        process_rgb(input_file)
        
    elif mode == 'help':
        show_help()
        
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Valid modes: 'grayscale' or 'rgb'")
        show_help()

if __name__ == '__main__':
    main()