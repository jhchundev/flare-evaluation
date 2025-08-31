#!/usr/bin/env python3
"""
Basic example of using the flare evaluation system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flare_evaluation import FlareEvaluator, FlareVisualizer
from flare_evaluation.config import ConfigManager


def main():
    """Run basic flare evaluation example."""
    
    # Set up configuration
    config = ConfigManager()
    config.set('evaluation.signal_threshold', 10)
    config.set('evaluation.light_threshold', 250)
    
    # Create evaluator
    evaluator = FlareEvaluator(config.export_section('evaluation'))
    
    # Load sample data
    data_path = '../data/sample_data.csv'
    print(f"Loading data from {data_path}...")
    
    # Perform evaluation
    results = evaluator.evaluate_file(data_path)
    
    # Display results
    print("\n" + "="*50)
    print("FLARE EVALUATION RESULTS")
    print("="*50)
    print(f"Flare Value: {results['flare_value']:.4f}")
    print(f"Total Signal: {results['sigma_value']:.2f}")
    print(f"Affected Pixels: {results['signal_pixel_count']}")
    print(f"Coverage: {results['flare_coverage_percent']:.2f}%")
    
    # Generate visualization
    visualizer = FlareVisualizer()
    mask = visualizer.create_flare_mask(
        evaluator.data_loader.load_csv(data_path),
        config.export_section('evaluation')
    )
    
    output_path = '../output/example_flare_mask.pgm'
    visualizer.save_visualization(mask, output_path, 'pgm')
    print(f"\nVisualization saved to {output_path}")
    
    # Get advanced metrics
    advanced = evaluator.get_detailed_metrics()
    if advanced:
        quality = advanced.get('quality', {})
        print(f"\nQuality Assessment: Grade {quality.get('quality_grade', 'N/A')}")


if __name__ == '__main__':
    main()