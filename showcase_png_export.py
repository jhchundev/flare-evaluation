#!/usr/bin/env python3
"""
Showcase PNG export capabilities with different modes and options.
"""

import os
import numpy as np
from flare_evaluation import FlareEvaluator, FlareDataGenerator, FlareVisualizer

def main():
    """Showcase PNG export capabilities."""
    print("="*60)
    print("PNG EXPORT SHOWCASE")
    print("="*60)
    
    # Generate sample data
    print("Generating sample flare data...")
    generator = FlareDataGenerator()
    generator.config.update({
        'flare_intensity_range': [0.3, 0.5],
        'flare_radius_range': [40, 60],
    })
    
    positions = [(150, 150), (350, 150), (250, 250), (150, 350), (350, 350)]
    data = generator.generate(positions)
    
    # Evaluate
    evaluator = FlareEvaluator()
    results = evaluator.evaluate(data)
    
    print(f"✓ Data: {data.shape}, Range: {data.min():.0f}-{data.max():.0f}")
    print(f"✓ Flare value: {results['flare_value']:.4f}")
    print(f"✓ Coverage: {results['flare_coverage_percent']:.2f}%")
    
    # PNG Export Showcase
    visualizer = FlareVisualizer()
    
    exports = [
        ("Basic composite", "composite.png", "composite", {}),
        ("Binary mask", "mask.png", "mask", {}),
        ("Viridis heatmap", "heatmap.png", "heatmap", {"colormap": "viridis"}),
        ("Jet colormap", "jet_colormap.png", "original", {"colormap": "jet"}),
        ("High-DPI composite", "high_dpi.png", "composite", {"dpi": 300}),
    ]
    
    print("\n" + "="*60)
    print("GENERATING PNG EXPORTS")
    print("="*60)
    
    os.makedirs('output/showcase', exist_ok=True)
    
    for description, filename, mode, options in exports:
        filepath = f'output/showcase/{filename}'
        visualizer.export_as_png(data, results, filepath, mode=mode, **options)
        
        size = os.path.getsize(filepath)
        print(f"✓ {description:20} → {filename:15} ({size:,} bytes)")
    
    # Multi-panel export
    print(f"\n✓ {'Multi-panel':20} → {'multi_panel.png':15}", end="")
    visualizer.export_multi_panel(
        data, results, 'output/showcase/multi_panel.png',
        panels=['original', 'mask', 'composite', 'heatmap'],
        layout=(2, 2)
    )
    size = os.path.getsize('output/showcase/multi_panel.png')
    print(f" ({size:,} bytes)")
    
    print("\n" + "="*60)
    print("CLI USAGE EXAMPLES")
    print("="*60)
    
    cli_examples = [
        "# Basic PNG export (default mode)",
        "python run_evaluator.py data.csv --plot result.png",
        "",
        "# Heatmap with jet colormap",
        "python run_evaluator.py data.csv --plot heatmap.png --png-mode heatmap --colormap jet",
        "",
        "# Multi-panel visualization",
        "python run_evaluator.py data.csv --plot analysis.png --png-mode multi --multi-layout 2 3",
        "",
        "# High-quality output",
        "python run_evaluator.py data.csv --plot quality.png --dpi 300 --compress-level 9",
        "",
        "# Different formats",
        "python run_evaluator.py data.csv --plot output.jpg --format jpg",
        "python run_evaluator.py data.csv --plot output.tiff --format tiff",
    ]
    
    for line in cli_examples:
        if line.startswith('#'):
            print(f"\n{line}")
        elif line.startswith('python'):
            print(f"  $ {line}")
        else:
            print(line)
    
    print("\n" + "="*60)
    print("PNG EXPORT MODES")
    print("="*60)
    
    modes = [
        ("composite", "RGB overlay with flare (yellow) and light sources (red)"),
        ("mask", "Binary mask showing only flare regions (white on black)"),
        ("heatmap", "Color-coded intensity visualization with colormaps"),
        ("original", "Original sensor data with optional colormap applied"),
        ("multi", "Multi-panel view combining multiple visualizations"),
    ]
    
    for mode, description in modes:
        print(f"  {mode:10} - {description}")
    
    print("\n" + "="*60)
    print("AVAILABLE COLORMAPS")
    print("="*60)
    
    colormaps = [
        ("viridis", "Purple-blue-green-yellow (perceptually uniform)"),
        ("jet", "Blue-cyan-yellow-red (high contrast)"),
        ("hot", "Black-red-yellow-white (heat-like)"),
        ("cool", "Cyan-magenta (cool tones)"),
        ("gray", "Grayscale (black to white)"),
    ]
    
    for cmap, description in colormaps:
        print(f"  {cmap:8} - {description}")
    
    print("\n" + "="*60)
    print("GENERATED FILES")
    print("="*60)
    
    # List all generated files
    files = os.listdir('output/showcase')
    png_files = [f for f in sorted(files) if f.endswith('.png')]
    
    total_size = 0
    for filename in png_files:
        filepath = f'output/showcase/{filename}'
        size = os.path.getsize(filepath)
        total_size += size
        print(f"  {filename:20} {size:8,} bytes")
    
    print(f"\n  Total: {len(png_files)} files, {total_size:,} bytes")
    print(f"\n📁 All files saved in: output/showcase/")
    
    if os.name == 'posix':  # macOS/Linux
        print(f"🖼️  View with: open output/showcase/")
    else:  # Windows
        print(f"🖼️  View with: start output/showcase/")

if __name__ == '__main__':
    main()