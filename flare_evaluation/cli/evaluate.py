"""
Command-line interface for flare evaluation.
"""

import argparse
import sys
import json
from pathlib import Path
import numpy as np

from ..core.evaluator import FlareEvaluator
from ..visualization.visualizer import FlareVisualizer
from ..config.config_manager import ConfigManager
from ..config.presets import PresetManager
from ..utils.validators import DataValidator


def main():
    """Main entry point for flare evaluation CLI."""
    parser = argparse.ArgumentParser(
        description='Advanced flare evaluation tool for optical sensor data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.csv                    # Basic evaluation with defaults
  %(prog)s data.csv --preset scientific # Use scientific preset
  %(prog)s data.csv --config my.json   # Use custom configuration
  %(prog)s data.csv --plot output.pgm  # Generate visualization
        """
    )
    
    # Input arguments
    parser.add_argument('input', help='Path to sensor data CSV file')
    
    # Configuration options
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument('--config', help='Path to configuration JSON file')
    config_group.add_argument('--preset', choices=PresetManager.list_presets(),
                            help='Use a preset configuration')
    
    # Evaluation parameters
    eval_group = parser.add_argument_group('evaluation parameters')
    eval_group.add_argument('--offset', type=float, 
                          help='Sensor black level offset')
    eval_group.add_argument('--signal-threshold', type=float,
                          help='Minimum signal above offset for flare detection')
    eval_group.add_argument('--light-threshold', type=float,
                          help='Threshold for light source detection')
    eval_group.add_argument('--pixel-size', type=float,
                          help='Physical pixel size for area calculation')
    eval_group.add_argument('--light-amount', type=float,
                          help='Light amount for normalization')
    
    # Output options
    output_group = parser.add_argument_group('output options')
    output_group.add_argument('--plot', help='Save visualization to file')
    output_group.add_argument('--format', choices=['pgm', 'ppm', 'png', 'jpg', 'tiff'],
                            default='png', help='Visualization format (default: png)')
    output_group.add_argument('--results', help='Save detailed results to JSON file')
    output_group.add_argument('--report', help='Save text report to file')
    
    # PNG-specific options
    png_group = parser.add_argument_group('PNG export options')
    png_group.add_argument('--png-mode', 
                          choices=['composite', 'mask', 'heatmap', 'original', 'multi'],
                          default='composite',
                          help='PNG visualization mode')
    png_group.add_argument('--colormap',
                          choices=['viridis', 'jet', 'hot', 'cool', 'gray'],
                          help='Colormap for visualization')
    png_group.add_argument('--dpi', type=int, default=100,
                          help='DPI for PNG output (default: 100)')
    png_group.add_argument('--compress-level', type=int, default=6,
                          choices=range(0, 10),
                          help='PNG compression level 0-9 (default: 6)')
    png_group.add_argument('--multi-layout', nargs=2, type=int, metavar=('ROWS', 'COLS'),
                          default=[2, 2],
                          help='Layout for multi-panel export (default: 2 2)')
    
    # Processing options
    proc_group = parser.add_argument_group('processing options')
    proc_group.add_argument('--validate', action='store_true',
                          help='Validate input data before processing')
    proc_group.add_argument('--verbose', '-v', action='store_true',
                          help='Enable verbose output')
    proc_group.add_argument('--quiet', '-q', action='store_true',
                          help='Suppress all output except errors')
    
    args = parser.parse_args()
    
    # Set up configuration
    config_manager = ConfigManager()
    
    if args.config:
        config_manager.load(args.config)
    
    if args.preset:
        PresetManager.apply_preset(config_manager, args.preset)
    
    # Override with command-line arguments
    if args.offset is not None:
        config_manager.set('evaluation.offset', args.offset)
    if args.signal_threshold is not None:
        config_manager.set('evaluation.signal_threshold', args.signal_threshold)
    if args.light_threshold is not None:
        config_manager.set('evaluation.light_threshold', args.light_threshold)
    if args.pixel_size is not None:
        config_manager.set('evaluation.pixel_size', args.pixel_size)
    if args.light_amount is not None:
        config_manager.set('evaluation.light_amount', args.light_amount)
    
    # Validate configuration
    validation = config_manager.validate()
    if not validation['valid']:
        print("Configuration errors:", file=sys.stderr)
        for error in validation['errors']:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose and validation['warnings']:
        print("Configuration warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Create evaluator with configuration
    evaluator = FlareEvaluator(config_manager.export_section('evaluation'))
    
    # Load and validate data
    try:
        if args.verbose:
            print(f"Loading data from {args.input}...")
        
        data = evaluator.data_loader.load_csv(args.input)
        
        if args.validate:
            validator = DataValidator()
            data_validation = validator.validate_sensor_data(
                data, 
                bit_depth=config_manager.get('sensor.bit_depth', 10)
            )
            
            if not data_validation['valid']:
                print("Data validation errors:", file=sys.stderr)
                for error in data_validation['errors']:
                    print(f"  - {error}", file=sys.stderr)
                sys.exit(1)
            
            if args.verbose:
                print(f"Data shape: {data_validation['info']['shape']}")
                print(f"Data range: {data_validation['info']['range']}")
    
    except Exception as e:
        print(f"Error loading data: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Perform evaluation
    try:
        if args.verbose:
            print("Performing flare evaluation...")
        
        results = evaluator.evaluate(data)
        
    except Exception as e:
        print(f"Error during evaluation: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate visualization if requested
    if args.plot:
        try:
            if args.verbose:
                print(f"Generating visualization: {args.plot}")
                print(f"  Format: {args.format}")
                if args.format == 'png':
                    print(f"  Mode: {args.png_mode}")
                    if args.colormap:
                        print(f"  Colormap: {args.colormap}")
            
            visualizer = FlareVisualizer()
            
            if args.format == 'pgm':
                # Classic PGM output
                mask = results['flare_mask']
                visualizer.save_visualization(mask, args.plot, 'pgm')
                
            elif args.format == 'png':
                # Advanced PNG output with options
                if args.png_mode == 'multi':
                    # Multi-panel export
                    visualizer.export_multi_panel(
                        data, results, args.plot,
                        layout=tuple(args.multi_layout)
                    )
                else:
                    # Single panel PNG export
                    visualizer.export_as_png(
                        data, results, args.plot,
                        mode=args.png_mode,
                        colormap=args.colormap,
                        dpi=args.dpi,
                        compress_level=args.compress_level
                    )
                    
            elif args.format in ['jpg', 'jpeg']:
                # JPEG output
                composite = visualizer.create_composite_visualization(data, results)
                visualizer.save_visualization(
                    composite, args.plot, args.format,
                    quality=95, optimize=True, dpi=args.dpi
                )
                
            elif args.format == 'tiff':
                # TIFF output
                composite = visualizer.create_composite_visualization(data, results)
                visualizer.save_visualization(
                    composite, args.plot, args.format,
                    compression='tiff_lzw', dpi=args.dpi
                )
                
            else:
                # Generic format
                composite = visualizer.create_composite_visualization(data, results)
                visualizer.save_visualization(composite, args.plot, args.format)
            
            if args.verbose:
                print(f"Visualization saved successfully")
                
        except Exception as e:
            print(f"Error generating visualization: {e}", file=sys.stderr)
    
    # Save detailed results if requested
    if args.results:
        try:
            # Prepare results for JSON serialization
            json_results = {
                'flare_value': float(results['flare_value']),
                'sigma_value': float(results['sigma_value']),
                'signal_pixel_count': int(results['signal_pixel_count']),
                'light_pixel_count': int(results['light_pixel_count']),
                'mean_flare_intensity': float(results['mean_flare_intensity']),
                'max_flare_intensity': float(results['max_flare_intensity']),
                'flare_coverage_percent': float(results['flare_coverage_percent']),
            }
            
            with open(args.results, 'w') as f:
                json.dump(json_results, f, indent=2)
            
            if args.verbose:
                print(f"Results saved to {args.results}")
                
        except Exception as e:
            print(f"Error saving results: {e}", file=sys.stderr)
    
    # Save text report if requested
    if args.report:
        try:
            evaluator.data_loader.data_writer.save_results(results, args.report)
            if args.verbose:
                print(f"Report saved to {args.report}")
        except Exception as e:
            print(f"Error saving report: {e}", file=sys.stderr)
    
    # Display results (unless quiet mode)
    if not args.quiet:
        print(f"\n{'='*50}")
        print("FLARE EVALUATION RESULTS")
        print('='*50)
        print(f"Flare Value: {results['flare_value']:.4f}")
        print(f"Total Signal: {results['sigma_value']:.2f}")
        print(f"Flare Pixels: {results['signal_pixel_count']}")
        print(f"Direct Illumination Pixels: {results.get('direct_illumination_pixel_count', 'N/A')}")
        print(f"Light Source Core Pixels: {results['light_pixel_count']}")
        print(f"Flare Coverage: {results['flare_coverage_percent']:.2f}%")
        print(f"Direct Illumination Coverage: {results.get('direct_illumination_coverage_percent', 0.0):.2f}%")
        
        # Get advanced metrics if verbose
        if args.verbose:
            advanced = evaluator.get_detailed_metrics()
            if advanced:
                print(f"\nQuality Assessment:")
                quality = advanced.get('quality', {})
                print(f"  Grade: {quality.get('quality_grade', 'N/A')}")
                print(f"  Quality Index: {quality.get('quality_index', 0):.3f}")
                print(f"  Severity Score: {quality.get('severity_score', 0):.3f}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())