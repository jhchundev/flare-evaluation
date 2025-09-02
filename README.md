# Flare Evaluation System

A resolution-independent Python tool for evaluating optical flare in image sensor data with three comprehensive metrics.

## 🔬 Three Resolution-Independent Metrics

### 1. **F_raw** - Raw Flare Intensity
```
F_raw = Σ(pixel_value - offset) / (N × pixel_area_µm²)
```
- **Units**: ADU/µm²
- **Purpose**: Absolute flare intensity per unit physical area
- **Use case**: Comparing absolute flare levels with proper physical units

### 2. **F_norm** - Area-Normalized Flare Ratio
```
F_norm = F_raw_flare / F_raw_direct_illumination
```
- **Units**: Dimensionless
- **Purpose**: Flare strength relative to direct illumination
- **Use case**: Cross-sensor comparison, independent of exposure/gain

### 3. **F_final** - Coverage-Weighted Flare Index
```
F_final = F_norm × (N_flare / N_sensor)^β
```
- **Units**: Dimensionless
- **Purpose**: Overall flare quality including spatial coverage
- **Use case**: Comprehensive flare assessment with coverage penalty

## ⚡ Quick Start

```bash
# Install
pip install -e .

# Evaluate sensor data
python flare.py evaluate data/sensor_data.csv

# Generate synthetic data
python flare.py generate output.csv

# Run with physical parameters
python flare.py evaluate data.csv --pixel-pitch 2.4 --output results.json
```

## 📊 Key Features

- ✅ **Resolution-Independent**: Proper pixel pitch handling in micrometers
- ✅ **Three Metrics**: Raw intensity, normalized ratio, and coverage-weighted index  
- ✅ **Physical Units**: ADU/µm² for absolute measurements
- ✅ **Cross-Sensor Comparison**: Dimensionless metrics for fair comparison
- ✅ **Automatic Normalization**: Against direct illumination or light source

## 🎯 Pixel Selection Criteria

Pixels are classified into regions based on intensity thresholds:

```
Background:    value ≤ (offset + signal_threshold)
Flare:         (offset + signal_threshold) < value ≤ direct_illumination_threshold  
Direct Light:  direct_illumination_threshold < value ≤ light_threshold
Light Source:  value > light_threshold
```

Default thresholds:
- `offset`: 64 ADU (sensor black level)
- `signal_threshold`: 10 ADU  
- `direct_illumination_threshold`: 400 ADU
- `light_threshold`: 600 ADU

## 🔧 Command Line Interface

```bash
# Basic evaluation
python flare.py evaluate <input.csv> [options]

Options:
  --pixel-pitch FLOAT      Pixel pitch in micrometers (default: 2.4)
  --offset INT            Sensor black level (default: 64)
  --signal-threshold INT   Minimum signal above offset (default: 10)
  --light-threshold INT    Light source threshold (default: 600)
  --output FILE           Save results to JSON file
  --plot FILE             Generate visualization
  --verbose               Show detailed output

# Data generation
python flare.py generate <output.csv> [options]

Options:
  --size INT              Sensor array size (default: 512)
  --bit-depth INT         Sensor bit depth (default: 10)
  --lights INT            Number of light sources
  --pixel-pitch FLOAT     Pixel pitch for simulation
```

## 📈 Python API

```python
from flare_evaluation import FlareEvaluator

# Create evaluator with proper pixel pitch
evaluator = FlareEvaluator({
    'pixel_pitch_um': 2.4,  # Smartphone sensor
    'offset': 64,
    'signal_threshold': 10
})

# Evaluate
results = evaluator.evaluate_file('sensor_data.csv')

# Access metrics
print(f"F_raw: {results['F_raw']:.4f} ADU/µm²")
print(f"F_norm: {results['F_norm']:.4f} (dimensionless)")
print(f"F_final: {results['F_final']:.6f} (dimensionless)")
```

## 🔍 Common Pixel Pitches

| Device Type | Typical Pixel Pitch | Example |
|------------|-------------------|---------|
| Smartphone | 1.0 - 1.4 µm | iPhone 14 Pro: 1.22 µm |
| Mirrorless | 3.5 - 4.5 µm | Sony A7R V: 3.76 µm |
| DSLR | 4.0 - 8.5 µm | Canon 5D IV: 6.72 µm |
| Medium Format | 5.0 - 9.0 µm | Hasselblad X2D: 5.3 µm |

## 🎨 Visualization

Color mapping in visualizations:
- **Yellow**: Flare regions (evaluation target)
- **Orange**: Direct illumination (transition zone)
- **Red**: Light source cores
- **Black/Gray**: Background below threshold

## 📦 Project Structure

```
flare_evaluation/
├── core/           # Core evaluation algorithms
├── visualization/  # Plotting and visualization
├── config/        # Configuration management
├── data_generation/ # Synthetic data generation
├── utils/         # Utilities
└── cli/           # Command-line interfaces
```

## ⚠️ Important Notes

1. **Always specify pixel pitch** for meaningful cross-sensor comparison
2. **F_norm and F_final** are resolution-independent (use for comparison)
3. **F_raw** varies with pixel size (use for absolute measurements)
4. Legacy `flare_value` with `pixel_size=1.0` is **deprecated**

## 📄 License

MIT License

## 📧 Contact

For questions or issues, please open a GitHub issue.