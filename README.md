# Flare Evaluation System - Enterprise Edition

A comprehensive, modular Python toolkit for advanced optical flare analysis in sensor data. Designed for professional image sensor evaluation with sophisticated algorithms, configurable presets, and extensive visualization capabilities.

## Features

- **Advanced Flare Detection**: Multi-threshold algorithms for precise flare quantification
- **Modular Architecture**: Clean separation of concerns with specialized modules
- **Configuration Management**: Flexible JSON-based configuration with preset support
- **Synthetic Data Generation**: Realistic flare pattern simulation with multiple models
- **Comprehensive Visualization**: Multiple visualization modes including heatmaps and 3D surfaces
- **Batch Processing**: Efficient processing of multiple sensor data files
- **Multiple Sensor Support**: 8-bit to 16-bit sensor compatibility
- **Quality Assessment**: Automated grading and quality metrics

## Project Structure

```
flare-evaluation/
├── flare_evaluation/           # Main package
│   ├── __init__.py
│   ├── core/                   # Core evaluation algorithms
│   │   ├── evaluator.py        # Main evaluation engine
│   │   └── metrics.py          # Advanced metrics calculation
│   ├── data_generation/        # Synthetic data generation
│   │   ├── generator.py        # Data generation engine
│   │   └── patterns.py         # Flare pattern algorithms
│   ├── visualization/          # Visualization tools
│   │   ├── visualizer.py       # Visualization engine
│   │   └── plotting.py         # Plot generation utilities
│   ├── config/                 # Configuration management
│   │   ├── config_manager.py   # Configuration system
│   │   └── presets.py          # Preset configurations
│   ├── utils/                  # Utility modules
│   │   ├── io.py              # I/O operations
│   │   ├── validators.py      # Data validation
│   │   └── converters.py      # Format converters
│   └── cli/                   # Command-line interfaces
│       ├── evaluate.py         # Evaluation CLI
│       └── generate.py         # Generation CLI
├── examples/                   # Example scripts
│   ├── basic_evaluation.py     # Basic usage example
│   ├── generate_test_data.py   # Data generation examples
│   └── batch_processing.py     # Batch processing example
├── data/                       # Data files
├── output/                     # Output directory
├── tests/                      # Test suite
├── docs/                       # Documentation
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── run_evaluator.py           # Quick evaluation script
└── generate_data.py           # Quick generation script
```

## Installation

### Standard Installation

```bash
# Clone the repository
git clone <repository-url>
cd flare-evaluation

# Install package in development mode
pip install -e .

# Or install with extras
pip install -e ".[visualization,advanced]"
```

### Dependencies

Core dependencies:
- `numpy >= 1.20.0`

Optional dependencies:
- `scipy` - Advanced metrics and spatial analysis
- `matplotlib` - Plotting capabilities
- `pillow` - Image format support

## Quick Start

### Basic Evaluation

```bash
# Using the CLI
python run_evaluator.py data/sample_data.csv --plot output/flare_mask.pgm

# With custom parameters
python run_evaluator.py data/sample_data.csv \
    --signal-threshold 10 \
    --light-threshold 250 \
    --plot output/result.pgm
```

### Generate Synthetic Data

```bash
# Generate standard 10-bit sensor data
python generate_data.py

# Generate with specific parameters
python generate_data.py output.csv --lights 5 --preset severe
```

### Python API Usage

```python
from flare_evaluation import FlareEvaluator, FlareDataGenerator

# Evaluation
evaluator = FlareEvaluator()
results = evaluator.evaluate_file('data/sensor_data.csv')
print(f"Flare Value: {results['flare_value']:.4f}")

# Data Generation
generator = FlareDataGenerator()
data = generator.generate(preset='standard')
generator.save(data, 'synthetic_data.csv')
```

## Configuration

### Using Configuration Files

Create a JSON configuration file:

```json
{
  "sensor": {
    "bit_depth": 10,
    "offset": 64
  },
  "evaluation": {
    "signal_threshold": 10,
    "light_threshold": 250
  }
}
```

Use with CLI:
```bash
python run_evaluator.py data.csv --config my_config.json
```

### Available Presets

- **standard**: Default evaluation for typical sensors
- **high_sensitivity**: Detect subtle flare effects
- **low_light**: Optimized for low-light conditions
- **high_dynamic_range**: HDR sensor evaluation
- **scientific**: High-precision scientific imaging
- **mobile_camera**: Smartphone camera sensors
- **automotive**: Automotive imaging sensors

Use presets:
```bash
python run_evaluator.py data.csv --preset scientific
```

## Advanced Features

### Batch Processing

Process multiple files:
```python
from examples.batch_processing import process_batch

process_batch('data/*.csv', 'output/batch_results')
```

### Custom Flare Patterns

```python
from flare_evaluation.data_generation import FlarePatternGenerator

pattern_gen = FlarePatternGenerator()
pattern_gen.add_radial_flare(data, x=250, y=250, radius=50)
pattern_gen.add_cross_pattern(data, x=250, y=250, length=100)
pattern_gen.add_ghosting(data, x=250, y=250, offset_x=50, offset_y=50)
```

### Quality Assessment

```python
evaluator = FlareEvaluator()
results = evaluator.evaluate_file('data.csv')
metrics = evaluator.get_detailed_metrics()

quality = metrics['quality']
print(f"Quality Grade: {quality['quality_grade']}")
print(f"Quality Index: {quality['quality_index']:.3f}")
```

## Algorithm Details

### Flare Detection Algorithm

1. **Light Source Detection**: Pixels above `light_threshold`
2. **Flare Region Detection**: Pixels between `signal_threshold + offset` and `light_threshold`
3. **Metric Calculation**:
   - Sum of target values: Σ(pixel_values - offset)
   - Flare value: Σ / (pixel_count × pixel_area) × light_amount

### Quality Metrics

- **Severity Score**: Normalized flare intensity (0-1)
- **Coverage Score**: Percentage of affected pixels
- **Quality Index**: Combined metric (0-1, higher is better)
- **Quality Grade**: A-F rating based on quality index

## Output Formats

### Evaluation Results

- **JSON**: Detailed metrics and statistics
- **PGM**: Grayscale visualization masks
- **Text Report**: Human-readable summary

### Visualization Options

- **Flare Mask**: Binary mask of detected flare regions
- **Composite View**: RGB overlay with flare and light sources
- **Intensity Heatmap**: Color-coded intensity visualization
- **Contour Map**: Intensity level contours

## Examples

See the `examples/` directory for:
- Basic evaluation workflow
- Synthetic data generation
- Batch processing multiple files
- Comparing preset configurations
- Custom visualization generation

## Command-Line Reference

### Evaluation

```bash
flare-evaluate [options] input.csv

Options:
  --preset PRESET           Use preset configuration
  --config CONFIG          Custom configuration file
  --signal-threshold N     Signal detection threshold
  --light-threshold N      Light source threshold
  --plot OUTPUT           Save visualization
  --format FORMAT         Output format (pgm, png, jpg)
  --results OUTPUT        Save JSON results
  --verbose              Verbose output
```

### Generation

```bash
flare-generate [options] output.csv

Options:
  --preset PRESET         Use preset (standard, minimal, severe)
  --size N               Sensor array size
  --bit-depth N          Sensor bit depth
  --lights N             Number of light sources
  --sequence N           Generate N frames
  --motion              Add motion to sequence
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=flare_evaluation tests/
```

### Code Style

```bash
# Format code
black flare_evaluation/

# Check style
flake8 flare_evaluation/

# Type checking
mypy flare_evaluation/
```

## Performance Considerations

- Default sensor size: 512×512 pixels
- Batch processing recommended for >10 files
- Downsample large arrays for visualization
- Use numpy arrays for efficient computation

## Troubleshooting

### Common Issues

1. **Memory errors with large files**: Reduce sensor size or use batch processing
2. **Missing dependencies**: Install with extras: `pip install -e ".[advanced]"`
3. **Visualization errors**: Ensure output directory exists

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]

## Citation

If you use this software in your research, please cite:
```
@software{flare_evaluation,
  title = {Flare Evaluation System},
  author = {Flare Evaluation Team},
  year = {2024},
  url = {https://github.com/yourusername/flare-evaluation}
}
```

## Contact

For questions or support, please open an issue on GitHub.