#!/usr/bin/env python3
"""
Demonstration of PNG export capabilities with various options.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from flare_evaluation import FlareEvaluator, FlareDataGenerator, FlareVisualizer
from flare_evaluation.config import ConfigManager


def generate_sample_data():
    """Generate sample data for demonstration."""
    print("Generating sample data...")
    generator = FlareDataGenerator()
    
    # Create data with prominent flare patterns
    config = {
        'flare_intensity_range': [0.3, 0.5],
        'flare_radius_range': [40, 60],
    }
    generator.config.update(config)
    
    # Multiple light sources for interesting visualization
    positions = [
        (150, 150),  # Top-left
        (350, 150),  # Top-right
        (250, 250),  # Center
        (150, 350),  # Bottom-left
        (350, 350),  # Bottom-right
    ]
    
    data = generator.generate(positions)
    print(f"  Generated {data.shape} array")
    print(f"  Data range: {data.min():.2f} - {data.max():.2f}")
    
    return data


def evaluate_data(data):
    """Evaluate the generated data."""
    print("\nEvaluating data...")
    evaluator = FlareEvaluator()
    results = evaluator.evaluate(data)
    
    print(f"  Flare value: {results['flare_value']:.4f}")
    print(f"  Affected pixels: {results['signal_pixel_count']}")
    print(f"  Coverage: {results['flare_coverage_percent']:.2f}%")
    
    return results


def demo_single_png_exports(data, results):
    """Demonstrate single PNG export modes."""
    print("\n" + "="*60)
    print("SINGLE PNG EXPORT MODES")
    print("="*60)
    
    visualizer = FlareVisualizer()
    output_dir = '../output/png_demo'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Composite visualization (default)
    print("\n1. Composite visualization (colored overlay)...")
    visualizer.export_as_png(
        data, results,
        f'{output_dir}/composite.png',
        mode='composite',
        dpi=150
    )
    print("   Saved: composite.png")
    
    # 2. Binary mask
    print("\n2. Binary flare mask...")
    visualizer.export_as_png(
        data, results,
        f'{output_dir}/mask.png',
        mode='mask',
        compress_level=9  # Maximum compression for binary data
    )
    print("   Saved: mask.png")
    
    # 3. Heatmap with viridis colormap
    print("\n3. Intensity heatmap (viridis)...")
    visualizer.export_as_png(
        data, results,
        f'{output_dir}/heatmap_viridis.png',
        mode='heatmap',
        colormap='viridis'
    )
    print("   Saved: heatmap_viridis.png")
    
    # 4. Original data with jet colormap
    print("\n4. Original data with jet colormap...")
    visualizer.export_as_png(
        data, results,
        f'{output_dir}/original_jet.png',
        mode='original',
        colormap='jet'
    )
    print("   Saved: original_jet.png")
    
    # 5. Original data with hot colormap
    print("\n5. Original data with hot colormap...")
    visualizer.export_as_png(
        data, results,
        f'{output_dir}/original_hot.png',
        mode='original',
        colormap='hot'
    )
    print("   Saved: original_hot.png")


def demo_multi_panel_export(data, results):
    """Demonstrate multi-panel PNG export."""
    print("\n" + "="*60)
    print("MULTI-PANEL PNG EXPORT")
    print("="*60)
    
    visualizer = FlareVisualizer()
    output_dir = '../output/png_demo'
    
    print("\nGenerating 2x2 multi-panel visualization...")
    visualizer.export_multi_panel(
        data, results,
        f'{output_dir}/multi_panel_2x2.png',
        panels=['original', 'mask', 'composite', 'heatmap'],
        layout=(2, 2)
    )
    print("   Saved: multi_panel_2x2.png")
    
    print("\nGenerating 1x4 horizontal strip...")
    visualizer.export_multi_panel(
        data, results,
        f'{output_dir}/multi_panel_strip.png',
        panels=['original', 'mask', 'heatmap', 'composite'],
        layout=(1, 4)
    )
    print("   Saved: multi_panel_strip.png")
    
    print("\nGenerating 3x2 comprehensive view...")
    visualizer.export_multi_panel(
        data, results,
        f'{output_dir}/multi_panel_3x2.png',
        panels=['original', 'mask', 'composite', 'heatmap', 'contour', 'heatmap'],
        layout=(3, 2)
    )
    print("   Saved: multi_panel_3x2.png")


def demo_colormap_variations(data, results):
    """Demonstrate different colormaps."""
    print("\n" + "="*60)
    print("COLORMAP VARIATIONS")
    print("="*60)
    
    visualizer = FlareVisualizer()
    output_dir = '../output/png_demo/colormaps'
    os.makedirs(output_dir, exist_ok=True)
    
    colormaps = ['viridis', 'jet', 'hot', 'cool', 'gray']
    
    print("\nGenerating heatmaps with different colormaps...")
    for cmap in colormaps:
        filepath = f'{output_dir}/heatmap_{cmap}.png'
        visualizer.export_as_png(
            data, results,
            filepath,
            mode='heatmap',
            colormap=cmap
        )
        print(f"   {cmap}: heatmap_{cmap}.png")


def demo_compression_levels(data, results):
    """Demonstrate PNG compression levels."""
    print("\n" + "="*60)
    print("PNG COMPRESSION COMPARISON")
    print("="*60)
    
    visualizer = FlareVisualizer()
    output_dir = '../output/png_demo/compression'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nGenerating PNGs with different compression levels...")
    print("(Lower compression = larger file, faster save)")
    print("(Higher compression = smaller file, slower save)")
    
    for level in [0, 3, 6, 9]:
        filepath = f'{output_dir}/compress_{level}.png'
        visualizer.export_as_png(
            data, results,
            filepath,
            mode='composite',
            compress_level=level
        )
        
        # Get file size
        size = os.path.getsize(filepath)
        print(f"   Level {level}: {size:,} bytes")


def demo_cli_commands():
    """Show example CLI commands."""
    print("\n" + "="*60)
    print("EXAMPLE CLI COMMANDS")
    print("="*60)
    
    examples = [
        ("Basic PNG export:",
         "python run_evaluator.py data.csv --plot output.png"),
        
        ("PNG with specific mode:",
         "python run_evaluator.py data.csv --plot output.png --png-mode heatmap"),
        
        ("PNG with colormap:",
         "python run_evaluator.py data.csv --plot output.png --png-mode heatmap --colormap jet"),
        
        ("High-quality PNG:",
         "python run_evaluator.py data.csv --plot output.png --dpi 300 --compress-level 9"),
        
        ("Multi-panel export:",
         "python run_evaluator.py data.csv --plot multi.png --png-mode multi --multi-layout 2 3"),
        
        ("JPEG export:",
         "python run_evaluator.py data.csv --plot output.jpg --format jpg"),
    ]
    
    for description, command in examples:
        print(f"\n{description}")
        print(f"  $ {command}")


def main():
    """Run all PNG export demonstrations."""
    print("="*60)
    print("PNG EXPORT DEMONSTRATION")
    print("="*60)
    
    # Generate and evaluate data
    data = generate_sample_data()
    results = evaluate_data(data)
    
    # Run demonstrations
    demo_single_png_exports(data, results)
    demo_multi_panel_export(data, results)
    demo_colormap_variations(data, results)
    demo_compression_levels(data, results)
    demo_cli_commands()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nAll PNG exports saved to: output/png_demo/")
    print("\nTo view the generated images:")
    print("  - On macOS: open output/png_demo/*.png")
    print("  - On Linux: xdg-open output/png_demo/*.png")
    print("  - On Windows: start output/png_demo")


if __name__ == '__main__':
    main()