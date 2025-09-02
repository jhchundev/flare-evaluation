# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Installation and Setup
```bash
# Install package in development mode with all dependencies
pip install -e ".[dev,visualization,advanced]"

# Install only core dependencies
pip install -e .
```

### Running the System
```bash
# Basic flare evaluation (single executable)
python flare.py evaluate data/sample_data.csv --pixel-pitch 2.4

# Generate synthetic test data  
python flare.py generate output.csv --size 512 --lights 3

# Evaluate with all options
python flare.py evaluate data.csv \
  --pixel-pitch 3.76 \
  --offset 64 \
  --signal-threshold 10 \
  --output results.json \
  --plot visualization.png \
  --matplotlib --mpl-plot all
```

### Development and Testing
```bash
# Format code
black flare_evaluation/

# Check code style
flake8 flare_evaluation/

# Type checking
mypy flare_evaluation/

# Run tests (when test suite is implemented)
pytest tests/ --cov=flare_evaluation
```

## Architecture Overview

### Core System Design
The flare evaluation system is built around a modular architecture with five main components:

1. **Core Engine** (`flare_evaluation.core/`): Contains the primary `FlareEvaluator` class and `FlareMetrics` for advanced calculations. The evaluator uses a multi-threshold algorithm to detect light sources (pixels > `light_threshold`) and flare regions (pixels between `signal_threshold + offset` and `light_threshold`).

2. **Data Generation** (`flare_evaluation.data_generation/`): The `FlareDataGenerator` creates realistic synthetic sensor data with configurable flare patterns. The `FlarePatternGenerator` implements various optical effects including radial flare, cross patterns, ghosting, and chromatic aberration.

3. **Configuration Management** (`flare_evaluation.config/`): Centralized configuration via `ConfigManager` with JSON support and `PresetManager` providing 9 built-in presets (standard, scientific, automotive, mobile_camera, etc.) for different sensor types and use cases.

4. **Visualization System** (`flare_evaluation.visualization/`): Advanced PNG/image export capabilities with multiple modes (composite, mask, heatmap, multi-panel) and colormap support (viridis, jet, hot, cool, gray).

5. **CLI Interfaces** (`flare_evaluation.cli/`): Command-line tools for evaluation and generation with extensive options for PNG export, compression, DPI settings, and batch processing.

### Data Flow Architecture
1. **Input**: CSV files containing 512×512 sensor data (typically 10-bit, 0-1023 range)
2. **Configuration**: JSON configs or presets define sensor parameters and thresholds
3. **Processing**: Core algorithms detect flare regions and calculate quality metrics
4. **Output**: Multiple formats including PNG visualizations, JSON results, and text reports

### Key Algorithms & Metrics

#### Three Resolution-Independent Metrics
1. **F_raw = Σ(pixel_value - offset) / (N × pixel_area_µm²)**
   - Raw flare intensity in ADU/µm²
   - Shows absolute flare per unit physical area

2. **F_norm = F_raw_flare / F_raw_direct_illumination**
   - Dimensionless ratio (resolution-independent)
   - Normalizes against reference illumination

3. **F_final = F_norm × (N_flare / N_sensor)^β**
   - Coverage-weighted index (β = 0.5 default)
   - Penalizes widespread flare

#### Pixel Classification
- **Background**: value ≤ (offset + signal_threshold)
- **Flare**: (offset + signal_threshold) < value ≤ direct_illumination_threshold
- **Direct Light**: direct_illumination_threshold < value ≤ light_threshold  
- **Light Source**: value > light_threshold

## Configuration System

### Hierarchical Configuration Structure
```json
{
  "sensor": {"bit_depth": 10, "offset": 64, "max_value": 1023},
  "evaluation": {"signal_threshold": 10, "light_threshold": 250},
  "generation": {"flare_intensity_range": [0.2, 0.4]},
  "visualization": {"output_format": "png", "colormap": "viridis"}
}
```

### Available Presets
The system includes preset configurations for:
- `standard`: Default 10-bit sensor evaluation
- `high_sensitivity`: Lower thresholds for subtle flare detection
- `scientific`: 16-bit high-precision sensors
- `mobile_camera`: Smartphone sensor optimization
- `automotive`: Automotive imaging sensors
- `high_dynamic_range`: HDR sensor support

## PNG Export System

### Advanced Visualization Modes
- **composite**: RGB overlay (flare=yellow, light sources=red)
- **mask**: Binary flare regions (optimized for small file sizes)
- **heatmap**: Intensity visualization with scientific colormaps
- **original**: Raw data with colormap application
- **multi**: Multi-panel analysis grids (configurable layouts)

### CLI PNG Options
```bash
--png-mode {composite,mask,heatmap,original,multi}
--colormap {viridis,jet,hot,cool,gray}
--dpi 300                    # High-resolution output
--compress-level 9           # Maximum compression
--multi-layout 2 3           # 2×3 panel grid
```

## Integration Points

### Python API Entry Points
```python
from flare_evaluation import FlareEvaluator, FlareDataGenerator, FlareVisualizer
from flare_evaluation.config import ConfigManager, PresetManager
```

### Legacy Compatibility
- `run_evaluator.py`: Wrapper for CLI evaluation
- `generate_data.py`: Wrapper for CLI generation
- `src/`: Legacy modules preserved for backward compatibility

### File Formats
- **Input**: CSV files with numerical sensor data (no headers)
- **Output**: PNG/PGM/PPM images, JSON results, text reports
- **Config**: JSON configuration files

## Development Notes

### Adding New Features
- New evaluation algorithms: Extend `FlareEvaluator` class in `core/evaluator.py`
- New visualization modes: Add methods to `FlareVisualizer` in `visualization/visualizer.py`
- New presets: Update `PresetManager.PRESETS` in `config/presets.py`
- New CLI options: Modify argument parsers in `cli/evaluate.py` or `cli/generate.py`

### Testing Strategy
Use `test_new_structure.py` to verify core functionality across all modules. The system includes validation functions in `utils/validators.py` for data integrity checks.

### Performance Considerations
- Default 512×512 arrays (~262K pixels)
- Batch processing recommended for >10 files
- PNG compression levels 0-9 for size/speed tradeoffs
- Multi-panel exports can be memory intensive for large arrays