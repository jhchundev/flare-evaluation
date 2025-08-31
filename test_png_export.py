#!/usr/bin/env python3
"""
Test PNG export functionality.
"""

import sys
import os
import numpy as np
from flare_evaluation import FlareEvaluator, FlareDataGenerator, FlareVisualizer

def test_png_export():
    """Test PNG export capabilities."""
    print("Testing PNG export functionality...")
    
    # Generate test data
    generator = FlareDataGenerator()
    data = generator.generate()
    print(f"✓ Generated test data: {data.shape}")
    
    # Evaluate data
    evaluator = FlareEvaluator()
    results = evaluator.evaluate(data)
    print(f"✓ Evaluated data: flare value = {results['flare_value']:.4f}")
    
    # Test PNG export modes
    visualizer = FlareVisualizer()
    output_dir = 'output/test_png'
    os.makedirs(output_dir, exist_ok=True)
    
    # Test 1: Basic composite PNG
    try:
        visualizer.export_as_png(
            data, results,
            f'{output_dir}/test_composite.png',
            mode='composite'
        )
        print("✓ Composite PNG export successful")
    except Exception as e:
        print(f"✗ Composite PNG export failed: {e}")
        return False
    
    # Test 2: Mask PNG
    try:
        visualizer.export_as_png(
            data, results,
            f'{output_dir}/test_mask.png',
            mode='mask'
        )
        print("✓ Mask PNG export successful")
    except Exception as e:
        print(f"✗ Mask PNG export failed: {e}")
        return False
    
    # Test 3: Heatmap with colormap
    try:
        visualizer.export_as_png(
            data, results,
            f'{output_dir}/test_heatmap.png',
            mode='heatmap',
            colormap='viridis'
        )
        print("✓ Heatmap PNG export successful")
    except Exception as e:
        print(f"✗ Heatmap PNG export failed: {e}")
        return False
    
    # Test 4: Multi-panel export
    try:
        visualizer.export_multi_panel(
            data, results,
            f'{output_dir}/test_multi.png',
            layout=(2, 2)
        )
        print("✓ Multi-panel PNG export successful")
    except Exception as e:
        print(f"✗ Multi-panel PNG export failed: {e}")
        return False
    
    # Test 5: Different compression levels
    try:
        for level in [0, 6, 9]:
            visualizer.export_as_png(
                data, results,
                f'{output_dir}/test_compress_{level}.png',
                mode='composite',
                compress_level=level
            )
        print("✓ Compression level options successful")
    except Exception as e:
        print(f"✗ Compression level test failed: {e}")
        return False
    
    # Check file sizes
    files = os.listdir(output_dir)
    png_files = [f for f in files if f.endswith('.png')]
    print(f"✓ Created {len(png_files)} PNG files")
    
    for filename in sorted(png_files):
        filepath = os.path.join(output_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes")
    
    return True

def test_cli_png_export():
    """Test PNG export through CLI."""
    print("\nTesting CLI PNG export...")
    
    # Test basic PNG export
    cmd = "python run_evaluator.py data/sample_data.csv --plot output/test_cli.png --verbose"
    result = os.system(cmd)
    
    if result == 0 and os.path.exists('output/test_cli.png'):
        print("✓ CLI PNG export successful")
        size = os.path.getsize('output/test_cli.png')
        print(f"  File size: {size:,} bytes")
        return True
    else:
        print("✗ CLI PNG export failed")
        return False

def main():
    """Run PNG export tests."""
    print("="*60)
    print("PNG EXPORT TESTING")
    print("="*60)
    
    success = True
    
    # Test 1: Direct API
    if not test_png_export():
        success = False
    
    # Test 2: CLI interface
    if not test_cli_png_export():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("ALL PNG EXPORT TESTS PASSED! ✓")
    else:
        print("SOME PNG EXPORT TESTS FAILED! ✗")
    print("="*60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())