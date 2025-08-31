#!/usr/bin/env python3
"""
Example of batch processing multiple sensor data files.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import glob
import json
import numpy as np
from pathlib import Path

from flare_evaluation import FlareEvaluator
from flare_evaluation.config import ConfigManager, PresetManager
from flare_evaluation.visualization import PlotGenerator


def process_batch(input_pattern='../data/*.csv', output_dir='../output/batch'):
    """
    Process multiple CSV files and generate summary statistics.
    
    Args:
        input_pattern: Glob pattern for input files
        output_dir: Directory for output results
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up evaluator
    config = ConfigManager()
    evaluator = FlareEvaluator(config.export_section('evaluation'))
    
    # Find all matching files
    files = sorted(glob.glob(input_pattern))
    
    if not files:
        print(f"No files found matching pattern: {input_pattern}")
        return
    
    print(f"Processing {len(files)} files...")
    print("="*60)
    
    # Store results for summary
    all_results = []
    
    for filepath in files:
        filename = Path(filepath).name
        print(f"\nProcessing: {filename}")
        
        try:
            # Evaluate file
            results = evaluator.evaluate_file(filepath)
            
            # Store key metrics
            summary = {
                'filename': filename,
                'flare_value': results['flare_value'],
                'signal_pixels': results['signal_pixel_count'],
                'coverage_percent': results['flare_coverage_percent'],
            }
            
            all_results.append(summary)
            
            # Save individual results
            result_file = os.path.join(output_dir, f"{Path(filename).stem}_results.json")
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2, default=float)
            
            print(f"  Flare value: {results['flare_value']:.4f}")
            print(f"  Coverage: {results['flare_coverage_percent']:.2f}%")
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    # Generate summary statistics
    if all_results:
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        
        flare_values = [r['flare_value'] for r in all_results]
        coverages = [r['coverage_percent'] for r in all_results]
        
        print(f"Files processed: {len(all_results)}")
        print(f"\nFlare Value Statistics:")
        print(f"  Mean: {np.mean(flare_values):.4f}")
        print(f"  Std: {np.std(flare_values):.4f}")
        print(f"  Min: {np.min(flare_values):.4f}")
        print(f"  Max: {np.max(flare_values):.4f}")
        
        print(f"\nCoverage Statistics:")
        print(f"  Mean: {np.mean(coverages):.2f}%")
        print(f"  Std: {np.std(coverages):.2f}%")
        print(f"  Min: {np.min(coverages):.2f}%")
        print(f"  Max: {np.max(coverages):.2f}%")
        
        # Save summary
        summary_file = os.path.join(output_dir, 'batch_summary.json')
        with open(summary_file, 'w') as f:
            json.dump({
                'files_processed': len(all_results),
                'results': all_results,
                'statistics': {
                    'flare_value': {
                        'mean': float(np.mean(flare_values)),
                        'std': float(np.std(flare_values)),
                        'min': float(np.min(flare_values)),
                        'max': float(np.max(flare_values)),
                    },
                    'coverage_percent': {
                        'mean': float(np.mean(coverages)),
                        'std': float(np.std(coverages)),
                        'min': float(np.min(coverages)),
                        'max': float(np.max(coverages)),
                    },
                },
            }, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")


def compare_presets(test_file='../data/sample_data.csv'):
    """
    Compare evaluation results using different presets.
    
    Args:
        test_file: Test file to evaluate
    """
    print("="*60)
    print("COMPARING PRESET CONFIGURATIONS")
    print("="*60)
    
    # Test different presets
    presets_to_test = ['standard', 'high_sensitivity', 'low_light']
    
    results_comparison = []
    
    for preset_name in presets_to_test:
        print(f"\nTesting preset: {preset_name}")
        
        # Set up configuration with preset
        config = ConfigManager()
        PresetManager.apply_preset(config, preset_name)
        
        # Create evaluator
        evaluator = FlareEvaluator(config.export_section('evaluation'))
        
        # Evaluate
        results = evaluator.evaluate_file(test_file)
        
        # Store results
        results_comparison.append({
            'preset': preset_name,
            'flare_value': results['flare_value'],
            'signal_pixels': results['signal_pixel_count'],
            'config': config.export_section('evaluation'),
        })
        
        print(f"  Flare value: {results['flare_value']:.4f}")
        print(f"  Signal pixels: {results['signal_pixel_count']}")
    
    # Display comparison
    print("\n" + "="*60)
    print("PRESET COMPARISON RESULTS")
    print("="*60)
    
    print(f"{'Preset':<20} {'Flare Value':<15} {'Signal Pixels':<15}")
    print("-"*50)
    
    for result in results_comparison:
        print(f"{result['preset']:<20} "
              f"{result['flare_value']:<15.4f} "
              f"{result['signal_pixels']:<15}")


def main():
    """Run batch processing examples."""
    
    # Process all CSV files in data directory
    print("Example 1: Batch processing all CSV files")
    process_batch()
    
    print("\n" + "="*60 + "\n")
    
    # Compare different presets
    print("Example 2: Comparing preset configurations")
    compare_presets()


if __name__ == '__main__':
    main()