"""
Command-line interface for synthetic data generation.
"""

import argparse
import sys
from pathlib import Path

from ..data_generation.generator import FlareDataGenerator
from ..config.config_manager import ConfigManager
from ..config.presets import PresetManager


def main():
    """Main entry point for data generation CLI."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic sensor data with flare patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s output.csv                  # Generate with defaults
  %(prog)s output.csv --preset severe  # Use severe flare preset
  %(prog)s output.csv --lights 5       # Generate 5 light sources
  %(prog)s output.csv --sequence 10    # Generate 10 frame sequence
        """
    )
    
    # Output argument
    parser.add_argument('output', help='Output CSV file path')
    
    # Configuration options
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument('--config', help='Path to configuration JSON file')
    config_group.add_argument('--preset', 
                            choices=['standard', 'minimal', 'severe'],
                            help='Use a preset configuration')
    
    # Generation parameters
    gen_group = parser.add_argument_group('generation parameters')
    gen_group.add_argument('--size', type=int, default=512,
                         help='Sensor array size (default: 512)')
    gen_group.add_argument('--bit-depth', type=int, default=10,
                         help='Sensor bit depth (default: 10)')
    gen_group.add_argument('--lights', type=int,
                         help='Number of light sources')
    gen_group.add_argument('--offset', type=float, default=64,
                         help='Sensor black level offset')
    gen_group.add_argument('--noise', type=float, default=2,
                         help='Noise standard deviation')
    
    # Flare parameters
    flare_group = parser.add_argument_group('flare parameters')
    flare_group.add_argument('--flare-intensity', nargs=2, type=float,
                           metavar=('MIN', 'MAX'),
                           help='Flare intensity range')
    flare_group.add_argument('--flare-radius', nargs=2, type=int,
                           metavar=('MIN', 'MAX'),
                           help='Flare radius range')
    flare_group.add_argument('--no-cross', action='store_true',
                           help='Disable cross pattern')
    flare_group.add_argument('--no-hot-pixels', action='store_true',
                           help='Disable hot pixels')
    
    # Sequence options
    seq_group = parser.add_argument_group('sequence options')
    seq_group.add_argument('--sequence', type=int,
                         help='Generate sequence of N frames')
    seq_group.add_argument('--motion', action='store_true',
                         help='Add motion to light sources in sequence')
    
    # Other options
    parser.add_argument('--seed', type=int,
                      help='Random seed for reproducibility')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set random seed if specified
    if args.seed is not None:
        import numpy as np
        np.random.seed(args.seed)
    
    # Set up configuration
    config_manager = ConfigManager()
    
    if args.config:
        config_manager.load(args.config)
    
    # Apply preset if specified
    if args.preset:
        preset_config = {
            'standard': {},
            'minimal': {
                'generation': {
                    'flare_intensity_range': [0.1, 0.2],
                    'flare_radius_range': [20, 30],
                    'hot_pixel_count': 5,
                }
            },
            'severe': {
                'generation': {
                    'flare_intensity_range': [0.5, 0.8],
                    'flare_radius_range': [60, 100],
                    'hot_pixel_count': 100,
                }
            },
        }
        config_manager.update(preset_config[args.preset])
    
    # Override with command-line arguments
    config_manager.set('sensor.size', args.size)
    config_manager.set('sensor.bit_depth', args.bit_depth)
    config_manager.set('sensor.offset', args.offset)
    config_manager.set('sensor.noise_std', args.noise)
    
    if args.flare_intensity:
        config_manager.set('generation.flare_intensity_range', list(args.flare_intensity))
    if args.flare_radius:
        config_manager.set('generation.flare_radius_range', list(args.flare_radius))
    if args.no_cross:
        config_manager.set('generation.enable_cross_pattern', False)
    if args.no_hot_pixels:
        config_manager.set('generation.enable_hot_pixels', False)
    
    # Create generator with proper mapping
    sensor_config = config_manager.export_section('sensor')
    generation_config = config_manager.export_section('generation')
    
    # Map sensor config to generator expected keys
    gen_config = {
        'sensor_size': sensor_config.get('size', 512),
        'bit_depth': sensor_config.get('bit_depth', 10),
        'max_value': 2 ** sensor_config.get('bit_depth', 10) - 1,
        'offset': sensor_config.get('offset', 64),
        'noise_std': sensor_config.get('noise_std', 2),
        'light_intensity': 2 ** sensor_config.get('bit_depth', 10) - 1,
        **generation_config,
    }
    generator = FlareDataGenerator(gen_config)
    
    # Generate light positions if specified
    light_positions = None
    if args.lights:
        size = args.size
        import numpy as np
        
        # Generate random positions
        light_positions = []
        for _ in range(args.lights):
            x = np.random.randint(size // 8, size - size // 8)
            y = np.random.randint(size // 8, size - size // 8)
            light_positions.append((x, y))
    
    try:
        if args.sequence:
            # Generate sequence
            if args.verbose:
                print(f"Generating sequence of {args.sequence} frames...")
            
            frames = generator.generate_sequence(
                args.sequence,
                motion=args.motion
            )
            
            # Save frames
            output_path = Path(args.output)
            base_name = output_path.stem
            suffix = output_path.suffix
            
            for i, frame in enumerate(frames):
                frame_path = output_path.parent / f"{base_name}_{i:04d}{suffix}"
                generator.save(frame, str(frame_path))
                
                if args.verbose:
                    print(f"  Saved frame {i+1}/{args.sequence}: {frame_path}")
            
            print(f"Generated {args.sequence} frames")
            
        else:
            # Generate single frame
            if args.verbose:
                print(f"Generating synthetic data...")
            
            data = generator.generate(light_positions)
            
            # Save data
            generator.save(data, args.output)
            
            # Display statistics
            if args.verbose:
                import numpy as np
                print(f"\nGeneration complete:")
                print(f"  Output file: {args.output}")
                print(f"  Array size: {data.shape}")
                print(f"  Data range: {data.min():.2f} - {data.max():.2f}")
                print(f"  Mean value: {data.mean():.2f}")
                print(f"  Std deviation: {data.std():.2f}")
                
                # Count pixels in different ranges
                offset = args.offset
                flare_pixels = np.sum((data > offset + 10) & (data < 250))
                light_pixels = np.sum(data >= 1000)
                
                print(f"  Approximate flare pixels: {flare_pixels}")
                print(f"  Light source pixels: {light_pixels}")
            else:
                print(f"Generated {args.output}")
    
    except Exception as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        sys.exit(1)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())