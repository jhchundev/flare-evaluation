#!/usr/bin/env python3
"""
Flare Evaluation System - Main Entry Point
Resolution-independent optical flare analysis for image sensors.
"""

import sys
import argparse
import json
import numpy as np
from pathlib import Path


def main():
    """Main entry point for the flare evaluation system."""
    parser = argparse.ArgumentParser(
        prog='flare',
        description='Resolution-independent flare evaluation system with three comprehensive metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s evaluate data.csv                    # Basic evaluation with defaults
  %(prog)s evaluate data.csv --pixel-pitch 3.76 # Specify pixel pitch (mirrorless camera)
  %(prog)s generate output.csv --lights 5       # Generate synthetic data with 5 light sources
  %(prog)s evaluate data.csv --output results.json --plot visualization.png
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ============= EVALUATE COMMAND =============
    eval_parser = subparsers.add_parser(
        'evaluate',
        help='Evaluate flare in sensor data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Evaluate optical flare with three metrics:
  F_raw:   Raw flare intensity (ADU/µm²)
  F_norm:  Normalized flare ratio (dimensionless, resolution-independent)
  F_final: Coverage-weighted index (dimensionless, with spatial penalty)
        """
    )
    
    eval_parser.add_argument('input', help='Input CSV file with sensor data')
    
    # Physical parameters
    phys_group = eval_parser.add_argument_group('physical parameters')
    phys_group.add_argument('--pixel-pitch', type=float, default=2.4,
                           help='Pixel pitch in micrometers (default: 2.4 µm, typical smartphone)')
    phys_group.add_argument('--bit-depth', type=int, default=10,
                           help='Sensor bit depth (default: 10)')
    
    # Thresholds
    thresh_group = eval_parser.add_argument_group('detection thresholds')
    thresh_group.add_argument('--offset', type=int, default=64,
                            help='Sensor black level in ADU (default: 64)')
    thresh_group.add_argument('--signal-threshold', type=int, default=10,
                            help='Minimum signal above offset (default: 10 ADU)')
    thresh_group.add_argument('--direct-threshold', type=int, default=400,
                            help='Direct illumination threshold (default: 400 ADU)')
    thresh_group.add_argument('--light-threshold', type=int, default=600,
                            help='Light source core threshold (default: 600 ADU)')
    thresh_group.add_argument('--beta', type=float, default=0.5,
                            help='Coverage penalty exponent for F_final (default: 0.5)')
    
    # Output options
    output_group = eval_parser.add_argument_group('output options')
    output_group.add_argument('--output', '-o', help='Save results to JSON file')
    output_group.add_argument('--plot', '-p', help='Generate visualization PNG')
    output_group.add_argument('--format', choices=['json', 'csv', 'text'], default='json',
                            help='Output format (default: json)')
    output_group.add_argument('--verbose', '-v', action='store_true',
                            help='Show detailed output')
    output_group.add_argument('--quiet', '-q', action='store_true',
                            help='Suppress all output except errors')
    
    # Visualization options
    viz_group = eval_parser.add_argument_group('visualization options')
    viz_group.add_argument('--colormap', choices=['viridis', 'hot', 'jet', 'gray'],
                         default='viridis', help='Colormap for visualization')
    viz_group.add_argument('--matplotlib', action='store_true',
                         help='Use matplotlib for advanced plotting')
    viz_group.add_argument('--mpl-plot', 
                         choices=['heatmap', 'distribution', 'radial', 'quality', '3d', 'all'],
                         help='Type of matplotlib plot')
    
    # Configuration presets
    config_group = eval_parser.add_argument_group('configuration')
    config_group.add_argument('--preset', 
                            choices=['smartphone', 'mirrorless', 'dslr', 'scientific'],
                            help='Use sensor preset configuration')
    config_group.add_argument('--config', help='Load configuration from JSON file')
    
    # ============= GENERATE COMMAND =============
    gen_parser = subparsers.add_parser(
        'generate',
        help='Generate synthetic sensor data with flare',
        description='Create synthetic sensor data with configurable flare patterns'
    )
    
    gen_parser.add_argument('output', help='Output CSV file path')
    
    # Generation parameters
    gen_group = gen_parser.add_argument_group('generation parameters')
    gen_group.add_argument('--size', type=int, default=512,
                         help='Sensor array size (default: 512)')
    gen_group.add_argument('--bit-depth', type=int, default=10,
                         help='Sensor bit depth (default: 10)')
    gen_group.add_argument('--pixel-pitch', type=float, default=2.4,
                         help='Pixel pitch in micrometers')
    gen_group.add_argument('--lights', type=int, default=3,
                         help='Number of light sources (default: 3)')
    gen_group.add_argument('--offset', type=int, default=64,
                         help='Sensor black level')
    gen_group.add_argument('--noise', type=float, default=2.0,
                         help='Noise standard deviation')
    
    # Flare parameters
    flare_group = gen_parser.add_argument_group('flare parameters')
    flare_group.add_argument('--flare-intensity', nargs=2, type=float,
                           default=[0.3, 0.5], metavar=('MIN', 'MAX'),
                           help='Flare intensity range (default: 0.3 0.5)')
    flare_group.add_argument('--flare-radius', nargs=2, type=int,
                           default=[40, 60], metavar=('MIN', 'MAX'),
                           help='Flare radius range in pixels (default: 40 60)')
    flare_group.add_argument('--pattern', 
                           choices=['radial', 'cross', 'both'],
                           default='both',
                           help='Flare pattern type')
    
    gen_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    gen_parser.add_argument('--verbose', '-v', action='store_true')
    
    # ============= INFO COMMAND =============
    info_parser = subparsers.add_parser(
        'info',
        help='Show information about metrics and pixel pitches',
        description='Display information about flare metrics and common sensor specifications'
    )
    
    info_parser.add_argument('--metrics', action='store_true',
                           help='Show detailed metric descriptions')
    info_parser.add_argument('--sensors', action='store_true',
                           help='Show common sensor pixel pitches')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Import here to avoid slow startup
    from flare_evaluation import FlareEvaluator
    from flare_evaluation.data_generation import FlareDataGenerator
    from flare_evaluation.visualization import FlareVisualizer, MatplotlibPlotter
    
    # ============= EXECUTE EVALUATE =============
    if args.command == 'evaluate':
        # Apply preset if specified
        config = _get_config_from_preset(args.preset) if args.preset else {}
        
        # Override with command-line arguments
        config.update({
            'pixel_pitch_um': args.pixel_pitch,
            'offset': args.offset,
            'signal_threshold': args.signal_threshold,
            'direct_illumination_threshold': args.direct_threshold,
            'light_threshold': args.light_threshold,
            'beta_coverage': args.beta,
            'bit_depth': args.bit_depth,
            'max_value': (2 ** args.bit_depth) - 1,
        })
        
        # Load config file if specified
        if args.config:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        
        # Create evaluator
        evaluator = FlareEvaluator(config)
        
        # Load and evaluate data
        if args.verbose:
            print(f"Loading data from {args.input}...")
            print(f"Using pixel pitch: {config['pixel_pitch_um']} µm")
        
        try:
            results = evaluator.evaluate_file(args.input)
        except Exception as e:
            print(f"Error evaluating data: {e}", file=sys.stderr)
            return 1
        
        # Generate visualization if requested
        if args.plot:
            if args.verbose:
                print(f"Generating visualization: {args.plot}")
            
            if args.matplotlib and args.mpl_plot:
                # Use matplotlib
                plotter = MatplotlibPlotter()
                _generate_matplotlib_plots(plotter, results, args)
            else:
                # Use standard visualizer
                visualizer = FlareVisualizer()
                from flare_evaluation.utils.io import DataLoader
                loader = DataLoader()
                data = loader.load_csv(args.input)
                
                # Create composite visualization
                if args.plot.endswith('.png'):
                    visualizer.export_as_png(
                        data, results, args.plot,
                        mode='composite',
                        colormap=args.colormap
                    )
                else:
                    composite = visualizer.create_composite_visualization(data, results)
                    visualizer.save_visualization(composite, args.plot, 'png')
        
        # Save results if requested
        if args.output:
            _save_results(results, args.output, args.format)
            if args.verbose:
                print(f"Results saved to {args.output}")
        
        # Display results
        if not args.quiet:
            _display_results(results, args.verbose)
        
        return 0
    
    # ============= EXECUTE GENERATE =============
    elif args.command == 'generate':
        if args.seed:
            np.random.seed(args.seed)
        
        # Create configuration
        config = {
            'sensor_size': args.size,
            'bit_depth': args.bit_depth,
            'max_value': (2 ** args.bit_depth) - 1,
            'offset': args.offset,
            'noise_std': args.noise,
            'light_intensity': (2 ** args.bit_depth) - 1,
            'flare_intensity_range': args.flare_intensity,
            'flare_radius_range': args.flare_radius,
            'enable_cross_pattern': args.pattern in ['cross', 'both'],
            'enable_hot_pixels': False,
        }
        
        if args.verbose:
            print(f"Generating {args.size}x{args.size} sensor data...")
            print(f"Bit depth: {args.bit_depth}, Lights: {args.lights}")
        
        # Generate data
        generator = FlareDataGenerator(config)
        
        # Create light positions
        light_positions = []
        for _ in range(args.lights):
            x = np.random.randint(args.size // 8, args.size - args.size // 8)
            y = np.random.randint(args.size // 8, args.size - args.size // 8)
            light_positions.append((x, y))
        
        data = generator.generate(light_positions)
        
        # Save data
        generator.data_writer.save_csv(data, args.output)
        
        if args.verbose:
            print(f"Data saved to {args.output}")
            print(f"Shape: {data.shape}, Range: [{data.min():.0f}, {data.max():.0f}]")
        
        return 0
    
    # ============= EXECUTE INFO =============
    elif args.command == 'info':
        if args.metrics or (not args.metrics and not args.sensors):
            _show_metrics_info()
        
        if args.sensors:
            _show_sensors_info()
        
        return 0
    
    return 0


def _get_config_from_preset(preset):
    """Get configuration from preset name."""
    presets = {
        'smartphone': {
            'pixel_pitch_um': 1.22,  # iPhone 14 Pro
            'offset': 64,
            'signal_threshold': 10,
        },
        'mirrorless': {
            'pixel_pitch_um': 3.76,  # Sony A7R V
            'offset': 64,
            'signal_threshold': 10,
        },
        'dslr': {
            'pixel_pitch_um': 6.72,  # Canon 5D Mark IV
            'offset': 100,
            'signal_threshold': 15,
        },
        'scientific': {
            'pixel_pitch_um': 4.5,
            'offset': 200,
            'signal_threshold': 20,
            'bit_depth': 16,
        },
    }
    return presets.get(preset, {})


def _display_results(results, verbose=False):
    """Display evaluation results."""
    print("\n" + "="*60)
    print("FLARE EVALUATION RESULTS")
    print("="*60)
    
    # Three main metrics
    print("\n📊 Three Resolution-Independent Metrics:")
    print("-"*40)
    print(f"F_raw:   {results['F_raw']:.4f} ADU/µm²")
    print(f"F_norm:  {results['F_norm']:.4f} (dimensionless)")
    print(f"F_final: {results['F_final']:.6f} (dimensionless)")
    
    # Physical parameters
    print(f"\n🔬 Physical Parameters:")
    print(f"Pixel pitch: {results['pixel_pitch_um']:.2f} µm")
    print(f"Pixel area:  {results['pixel_area_um2']:.2f} µm²")
    
    # Statistics
    print(f"\n📈 Statistics:")
    print(f"Flare pixels: {results['signal_pixel_count']:,} ({results['coverage_ratio']*100:.2f}%)")
    print(f"Direct illumination pixels: {results['direct_illumination_pixel_count']:,}")
    print(f"Light source pixels: {results['light_pixel_count']:,}")
    
    if verbose:
        print(f"\n🔍 Detailed Metrics:")
        print(f"Coverage weight: {results['coverage_weight']:.4f}")
        print(f"Mean flare intensity: {results['mean_flare_intensity']:.2f} ADU")
        print(f"Max flare intensity: {results['max_flare_intensity']:.2f} ADU")
        print(f"Legacy flare value: {results['flare_value']:.4f} (deprecated)")
    
    print("="*60)


def _save_results(results, output_path, format='json'):
    """Save results to file."""
    # Remove non-serializable items
    save_data = {k: v for k, v in results.items() 
                 if not k.endswith('_mask')}
    
    # Convert numpy types
    for key in save_data:
        if isinstance(save_data[key], np.ndarray):
            save_data[key] = save_data[key].tolist()
        elif isinstance(save_data[key], (np.integer, np.floating)):
            save_data[key] = float(save_data[key])
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(save_data, f, indent=2)
    elif format == 'csv':
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value', 'Units'])
            writer.writerow(['F_raw', save_data['F_raw'], 'ADU/µm²'])
            writer.writerow(['F_norm', save_data['F_norm'], 'dimensionless'])
            writer.writerow(['F_final', save_data['F_final'], 'dimensionless'])
    elif format == 'text':
        with open(output_path, 'w') as f:
            f.write("FLARE EVALUATION RESULTS\n")
            f.write("="*40 + "\n")
            f.write(f"F_raw:   {save_data['F_raw']:.4f} ADU/µm²\n")
            f.write(f"F_norm:  {save_data['F_norm']:.4f}\n")
            f.write(f"F_final: {save_data['F_final']:.6f}\n")


def _generate_matplotlib_plots(plotter, results, args):
    """Generate matplotlib plots."""
    # Implementation would go here
    pass


def _show_metrics_info():
    """Show information about metrics."""
    print("\n" + "="*60)
    print("FLARE EVALUATION METRICS")
    print("="*60)
    
    print("""
📊 Three Resolution-Independent Metrics:

1. F_raw - Raw Flare Intensity
   Formula: Σ(pixel_value - offset) / (N × pixel_area_µm²)
   Units:   ADU/µm²
   Purpose: Absolute flare intensity per unit physical area
   
2. F_norm - Area-Normalized Flare Ratio
   Formula: F_raw_flare / F_raw_direct_illumination
   Units:   Dimensionless
   Purpose: Resolution-independent comparison across sensors
   
3. F_final - Coverage-Weighted Flare Index
   Formula: F_norm × (N_flare / N_sensor)^β
   Units:   Dimensionless
   Purpose: Overall quality with spatial coverage penalty

🎯 Pixel Classification Thresholds:
   Background:    value ≤ (offset + signal_threshold)
   Flare:         (offset + signal_threshold) < value ≤ direct_threshold
   Direct Light:  direct_threshold < value ≤ light_threshold
   Light Source:  value > light_threshold
""")


def _show_sensors_info():
    """Show information about common sensors."""
    print("\n" + "="*60)
    print("COMMON SENSOR SPECIFICATIONS")
    print("="*60)
    
    print("""
📷 Typical Pixel Pitches by Device Type:

Smartphones:
  iPhone 14 Pro:        1.22 µm
  Samsung S23 Ultra:    1.40 µm
  Google Pixel 8 Pro:   1.20 µm

Mirrorless Cameras:
  Sony A7R V:          3.76 µm
  Canon R5:            4.39 µm
  Nikon Z9:            4.35 µm

DSLR Cameras:
  Canon 5D Mark IV:    6.72 µm
  Nikon D850:          4.35 µm
  Canon 1DX Mark III:  8.20 µm

Medium Format:
  Hasselblad X2D:      5.30 µm
  Fujifilm GFX100:     3.76 µm
  Phase One IQ4:       4.60 µm

Scientific/Industrial:
  sCMOS typical:       6.50 µm
  CCD typical:         4.50-9.00 µm
""")


if __name__ == '__main__':
    sys.exit(main())