# RGB Flare Evaluation Tools

Extended tools for analyzing RGB sensor data with space-separated values format.

## RGB Data Format

Each CSV cell contains three space-separated values: `R G B`

Example CSV structure:
```
100 100 100,150 145 140,200 195 185,...
120 118 115,180 178 172,220 218 210,...
...
```

## New RGB Tools

### 1. Convert to RGB Format
```bash
python convert_to_rgb.py <input.csv> <output.csv> [--mode realistic]
```
Modes:
- `duplicate`: Simple R=G=B conversion
- `realistic`: Simulates chromatic effects in flare
- `warm`: Warm color temperature
- `cool`: Cool color temperature

### 2. Evaluate RGB Flare
```bash
python evaluate_flare_rgb.py <rgb.csv> --pixel-pitch 2.4 --output results.json
```
Features:
- Per-channel metrics (R, G, B)
- Combined luminance-weighted metrics
- Chromatic aberration detection
- Resolution-independent analysis

### 3. Generate RGB Data
```bash
python generate_data_rgb.py <output.csv> --lights 3 --chromatic --size 512
```
Options:
- `--chromatic`: Enable chromatic aberration simulation
- `--no-chromatic`: Disable chromatic effects
- Color temperature variations per light source

### 4. Visualize RGB Flare
```bash
python visualize_flare_rgb.py <rgb.csv> <output.png> --mode composite
```
Modes:
- `composite`: True-color RGB with flare enhancement
- `channels`: Side-by-side R, G, B channel view
- `mask`: Flare region masks per channel
- `chromatic`: Chromatic aberration analysis

## Example Workflow

```bash
# 1. Convert existing Gemini data to RGB
python convert_to_rgb.py data/gemini_flare_10bit.csv data/gemini_rgb.csv --mode realistic

# 2. Evaluate RGB flare metrics
python evaluate_flare_rgb.py data/gemini_rgb.csv --pixel-pitch 2.4

# 3. Generate synthetic RGB test data
python generate_data_rgb.py test_rgb.csv --lights 3 --chromatic

# 4. Visualize RGB channels
python visualize_flare_rgb.py test_rgb.csv output/channels.png --mode channels
```

## Key Metrics

### Per-Channel Analysis
- **F_raw**: Flare intensity per channel (ADU/µm²)
- **F_norm**: Normalized ratio per channel
- **F_final**: Coverage-weighted index per channel

### Chromatic Aberration Index
- `< 0.1`: Low chromatic aberration ✅
- `> 0.1`: Significant chromatic aberration ⚠️

## Verification Results

### Gemini Data (Converted to RGB)
- R Channel F_final: 0.0410
- G Channel F_final: 0.0423  
- B Channel F_final: 0.0447
- Chromatic Aberration: 0.036 (Low)

### Synthetic RGB Data (With Chromatic Aberration)
- R Channel F_final: 0.2704
- G Channel F_final: 0.3297
- B Channel F_final: 0.3457
- Chromatic Aberration: 0.103 (Significant)