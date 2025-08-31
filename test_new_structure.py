#!/usr/bin/env python3
"""
Test script to verify the new modular structure works correctly.
"""

import sys
import numpy as np
from flare_evaluation import FlareEvaluator, FlareDataGenerator, FlareVisualizer
from flare_evaluation.config import ConfigManager, PresetManager

def test_imports():
    """Test that all imports work."""
    print("✓ Imports successful")

def test_configuration():
    """Test configuration management."""
    config = ConfigManager()
    assert config.get('sensor.bit_depth') == 10
    
    config.set('sensor.bit_depth', 12)
    assert config.get('sensor.bit_depth') == 12
    
    print("✓ Configuration management working")

def test_data_generation():
    """Test data generation."""
    generator = FlareDataGenerator()
    data = generator.generate()
    
    assert data.shape == (512, 512)
    assert data.min() >= 0
    assert data.max() <= 1023
    
    print("✓ Data generation working")
    print(f"  Generated data shape: {data.shape}")
    print(f"  Data range: {data.min():.2f} - {data.max():.2f}")
    
    return data

def test_evaluation(data):
    """Test flare evaluation."""
    evaluator = FlareEvaluator()
    results = evaluator.evaluate(data)
    
    assert 'flare_value' in results
    assert 'signal_pixel_count' in results
    assert results['signal_pixel_count'] >= 0
    
    print("✓ Evaluation working")
    print(f"  Flare value: {results['flare_value']:.4f}")
    print(f"  Signal pixels: {results['signal_pixel_count']}")
    
    return results

def test_visualization(data, results):
    """Test visualization."""
    visualizer = FlareVisualizer()
    
    config = {'offset': 64, 'signal_threshold': 10, 'light_threshold': 250}
    mask = visualizer.create_flare_mask(data, config)
    
    assert mask.shape == data.shape
    assert mask.dtype == np.uint8
    
    print("✓ Visualization working")
    print(f"  Mask shape: {mask.shape}")

def test_presets():
    """Test preset configurations."""
    presets = PresetManager.list_presets()
    assert len(presets) > 0
    
    preset_config = PresetManager.get_preset('standard')
    assert 'evaluation' in preset_config or 'sensor' in preset_config
    
    print("✓ Presets working")
    print(f"  Available presets: {len(presets)}")

def main():
    """Run all tests."""
    print("="*60)
    print("TESTING NEW MODULAR STRUCTURE")
    print("="*60)
    
    try:
        test_imports()
        test_configuration()
        data = test_data_generation()
        results = test_evaluation(data)
        test_visualization(data, results)
        test_presets()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())