#!/usr/bin/env python3
"""
Example of generating synthetic sensor data with various flare patterns.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from flare_evaluation import FlareDataGenerator
from flare_evaluation.config import PresetManager


def generate_standard_test():
    """Generate standard test data."""
    print("Generating standard test data...")
    
    generator = FlareDataGenerator()
    
    # Generate with default settings
    data = generator.generate()
    generator.save(data, '../data/test_standard.csv')
    
    print(f"  Shape: {data.shape}")
    print(f"  Range: {data.min():.2f} - {data.max():.2f}")
    print(f"  Saved to: data/test_standard.csv")


def generate_severe_flare():
    """Generate data with severe flare."""
    print("\nGenerating severe flare test data...")
    
    # Use severe configuration
    config = {
        'flare_intensity_range': [0.5, 0.8],
        'flare_radius_range': [60, 100],
        'hot_pixel_count': 100,
    }
    
    generator = FlareDataGenerator(config)
    
    # Add many light sources
    positions = [
        (100, 100), (400, 100), (250, 250),
        (100, 400), (400, 400), (200, 350),
        (350, 200), (150, 250), (350, 350),
    ]
    
    data = generator.generate(positions)
    generator.save(data, '../data/test_severe.csv')
    
    print(f"  Light sources: {len(positions)}")
    print(f"  Saved to: data/test_severe.csv")


def generate_minimal_flare():
    """Generate data with minimal flare."""
    print("\nGenerating minimal flare test data...")
    
    config = {
        'flare_intensity_range': [0.1, 0.15],
        'flare_radius_range': [15, 25],
        'enable_cross_pattern': False,
        'hot_pixel_count': 0,
    }
    
    generator = FlareDataGenerator(config)
    
    # Just a few light sources
    positions = [(250, 250), (150, 150)]
    
    data = generator.generate(positions)
    generator.save(data, '../data/test_minimal.csv')
    
    print(f"  Light sources: {len(positions)}")
    print(f"  Saved to: data/test_minimal.csv")


def generate_motion_sequence():
    """Generate a sequence with moving light sources."""
    print("\nGenerating motion sequence...")
    
    generator = FlareDataGenerator()
    
    # Generate 10 frames with motion
    frames = generator.generate_sequence(10, motion=True)
    
    for i, frame in enumerate(frames):
        filepath = f'../data/sequence/frame_{i:04d}.csv'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        generator.save(frame, filepath)
    
    print(f"  Generated {len(frames)} frames")
    print(f"  Saved to: data/sequence/")


def generate_different_sensors():
    """Generate data for different sensor types."""
    print("\nGenerating data for different sensor types...")
    
    sensor_configs = {
        '8-bit': {'bit_depth': 8, 'max_value': 255, 'offset': 16},
        '10-bit': {'bit_depth': 10, 'max_value': 1023, 'offset': 64},
        '12-bit': {'bit_depth': 12, 'max_value': 4095, 'offset': 256},
        '14-bit': {'bit_depth': 14, 'max_value': 16383, 'offset': 512},
    }
    
    for name, config in sensor_configs.items():
        generator = FlareDataGenerator(config)
        data = generator.generate()
        
        filepath = f'../data/sensor_{name}.csv'
        generator.save(data, filepath)
        
        print(f"  {name}: range {data.min():.0f}-{data.max():.0f}")


def main():
    """Run all generation examples."""
    print("="*60)
    print("FLARE DATA GENERATION EXAMPLES")
    print("="*60)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Run all examples
    generate_standard_test()
    generate_severe_flare()
    generate_minimal_flare()
    generate_motion_sequence()
    generate_different_sensors()
    
    print("\n" + "="*60)
    print("All test data generated successfully!")


if __name__ == '__main__':
    main()