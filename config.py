#!/usr/bin/env python3
"""
Configuration for Flare Evaluation System
Edit this file to change parameters
"""

# Main configuration - EDIT THIS SECTION
CONFIG = {
    # Mode: 'grayscale' or 'rgb'
    'mode': 'grayscale',  # 'grayscale' for single value per cell, 'rgb' for R G B per cell
    
    # Input CSV file
    'input_file': 'data/gemini_flare_10bit.csv',
    
    # Output files (both generated automatically)
    'output_json': 'output/results.json',       # Metrics results
    'output_image': 'output/visualization.png',  # Visual output
    
    # Sensor parameters
    'pixel_pitch': 2.4,     # Pixel pitch in micrometers
    'offset': 64,           # Black level/offset in ADU
    
    # Flare detection thresholds
    'signal_threshold': 10,     # Minimum signal above offset
    'direct_threshold': 200,    # Direct illumination threshold  
    'light_threshold': 250,     # Light source threshold
    'beta': 0.5,                # Coverage weighting exponent
}

# Example configurations (uncomment to use):

# For RGB data analysis:
# CONFIG['mode'] = 'rgb'
# CONFIG['input_file'] = 'data/gemini_flare_rgb.csv'

# For smartphone sensor (2.4 µm pixels):
# CONFIG['pixel_pitch'] = 2.4

# For mirrorless sensor (3.76 µm pixels):
# CONFIG['pixel_pitch'] = 3.76

# For DSLR sensor (8.4 µm pixels):
# CONFIG['pixel_pitch'] = 8.4

# For scientific CCD (5.5 µm pixels):
# CONFIG['pixel_pitch'] = 5.5