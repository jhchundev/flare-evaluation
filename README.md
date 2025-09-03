# Flare Evaluation System

Simple Python tool for evaluating lens flare in image sensors.  
Just 2 files, 2 modes, 1 command!

## 🚀 Quick Start

```bash
# 1. Edit config.py to set mode and input file
# 2. Run analysis
python flare.py

# That's it! You get both metrics and visualization
```

## 📋 Ultra-Simple Design

**Just 2 files:**
- `flare.py` - The analysis tool
- `config.py` - Your settings

**Just 2 modes:**
- `'grayscale'` - Single value per cell (standard sensors)
- `'rgb'` - Three values per cell: R G B (color sensors)

**Both modes automatically generate:**
- ✅ JSON file with F_raw, F_norm, F_final metrics
- ✅ PNG visualization with color-coded flare regions

## 🎯 Configuration

Edit `config.py`:

```python
CONFIG = {
    'mode': 'grayscale',  # or 'rgb'
    'input_file': 'data/sensor_data.csv',
    'output_json': 'output/results.json',
    'output_image': 'output/visualization.png',
    'pixel_pitch': 2.4,  # Sensor pixel size in µm
    'offset': 64,        # Black level
}
```

## 📊 What You Get

### Metrics (in JSON)
- **F_raw** (ADU/µm²): Physical flare intensity
- **F_norm** (dimensionless): Normalized flare ratio  
- **F_final** (dimensionless): Coverage-weighted index

### 🔬 Flare Value Equations

The system calculates three key metrics to quantify lens flare:

#### 1. Raw Flare Intensity (F_raw)
```
F_raw = Σ(flare_pixels) / (N_flare × pixel_pitch²)
```
- `flare_pixels`: ADU values of pixels identified as flare
- `N_flare`: Number of flare pixels
- `pixel_pitch`: Sensor pixel size in micrometers
- **Units**: ADU/µm²

#### 2. Normalized Flare Ratio (F_norm)
```
F_norm = Σ(flare_pixels) / Σ(light_source_pixels)
```
- Ratio of total flare signal to total light source signal
- **Units**: Dimensionless (ratio)

#### 3. Final Flare Index (F_final)
```
F_final = F_norm × (1 + β × coverage_ratio)
coverage_ratio = N_flare / N_total
```
- `β`: Coverage weight parameter (default: 0.5)
- `coverage_ratio`: Fraction of sensor area affected by flare
- `N_total`: Total number of pixels
- **Units**: Dimensionless (weighted index)

### Visualization (PNG)
- 🟡 Yellow = Flare regions
- 🟠 Orange = Direct illumination
- 🔴 Red = Light sources
- ⚫ Dark = Background

## 💡 Examples

### Grayscale Analysis
```python
# config.py:
CONFIG = {
    'mode': 'grayscale',
    'input_file': 'data/gemini_flare_10bit.csv',
    'pixel_pitch': 2.4,  # Smartphone sensor
}
```
Run: `python flare.py`  
Get: `results.json` + `visualization.png`

### RGB Analysis
```python
# config.py:
CONFIG = {
    'mode': 'rgb',
    'input_file': 'data/gemini_flare_rgb.csv',
    'pixel_pitch': 2.4,
}
```
Run: `python flare.py`  
Get: Per-channel metrics + RGB visualization

## 🌈 Data Formats

**Grayscale CSV:**
```
100.5,150.2,200.8
120.3,180.5,210.1
```

**RGB CSV:** (R G B with flexible spacing)
```
100 100 100,150 145 140,200 195 185
100   100   100,150  145  140,200     195     185
```

## 📸 Common Pixel Pitches

| Sensor | Pixel Pitch |
|--------|------------|
| Smartphone | 2.4 µm |
| Mirrorless | 3.76 µm |
| DSLR | 8.4 µm |
| Scientific | 5.5 µm |

## 📦 Requirements

```bash
pip install numpy pillow
```

No YAML, no complex dependencies!

## ✅ Why This System?

- **2 files** instead of 8+ separate tools
- **2 modes** that cover all use cases  
- **1 command** does everything
- **0 YAML** files needed
- **Both outputs** (metrics + image) in one run
- **Same metrics** for grayscale and RGB

## 🔧 Full Config Reference

```python
CONFIG = {
    # Mode selection
    'mode': 'grayscale',     # or 'rgb'
    
    # Files
    'input_file': 'data/input.csv',
    'output_json': 'output/results.json',
    'output_image': 'output/visualization.png',
    
    # Sensor
    'pixel_pitch': 2.4,       # Micrometers
    'offset': 64,             # Black level ADU
    
    # Thresholds
    'signal_threshold': 10,   # Min signal
    'direct_threshold': 200,  # Direct light
    'light_threshold': 250,   # Light source
    'beta': 0.5,             # Coverage weight
}
```

## 📂 Project Structure

```
flare-evaluation/
├── flare.py        # Main tool
├── config.py       # Your settings
├── data/           # Input CSV files
└── output/         # Results (auto-created)
```

That's all you need!