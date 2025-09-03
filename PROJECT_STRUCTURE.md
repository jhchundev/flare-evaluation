# Project Structure - Flare Evaluation Tools

## 🎯 Reorganization Summary

### File Naming Convention
All Python files now follow a clear `flare_[action]_[type].py` pattern:

#### Before → After Renaming
- `evaluate_flare.py` → `flare_eval.py`
- `generate_data.py` → `flare_gen.py`
- `visualize_flare.py` → `flare_viz.py`
- `evaluate_flare_rgb.py` → `flare_eval_rgb.py`
- `generate_data_rgb.py` → `flare_gen_rgb.py`
- `visualize_flare_rgb.py` → `flare_viz_rgb.py`
- `convert_to_rgb.py` → `flare_convert_rgb.py`
- `flare_info.py` → `flare_help.py`

## 📁 Directory Organization

```
flare-evaluation/
│
├── 🔧 Main Tools (Root Directory)
│   ├── flare_eval.py         # Grayscale flare evaluation
│   ├── flare_gen.py          # Grayscale data generation
│   ├── flare_viz.py          # Grayscale visualization
│   ├── flare_eval_rgb.py     # RGB flare evaluation
│   ├── flare_gen_rgb.py      # RGB data generation
│   ├── flare_viz_rgb.py      # RGB visualization
│   ├── flare_convert_rgb.py  # Grayscale to RGB converter
│   └── flare_help.py         # Help and documentation
│
├── 📊 data/                  # Input Data
│   ├── gemini_flare_10bit.csv
│   ├── gemini_flare_rgb.csv
│   ├── sample_data.csv
│   └── *.json (results)
│
├── 🎨 output/                # Generated Outputs
│   ├── visualizations (*.png)
│   ├── results (*.json)
│   └── generated data (*.csv)
│
├── 🧪 tests/                 # Test Files
│   ├── test_*.csv
│   └── verify_spacing.py
│
├── 📚 examples/              # Example Scripts
│   └── sample workflows
│
├── 📦 archive/               # Old/Deprecated Files
│   └── previous versions
│
└── 📝 Documentation
    ├── README.md
    ├── RGB_TOOLS_README.md
    └── PROJECT_STRUCTURE.md

```

## 🔑 Key Improvements

### 1. **Consistent Naming**
- All tools start with `flare_` prefix
- Action verbs are shortened (eval, gen, viz)
- RGB tools clearly marked with `_rgb` suffix

### 2. **Clean Root Directory**
- Only main executable tools in root
- No test CSV files cluttering root
- Clear separation of concerns

### 3. **Organized Data Flow**
- Input: `data/` directory
- Processing: Root tools
- Output: `output/` directory
- Testing: `tests/` directory

### 4. **Tool Categories**

#### Grayscale Tools
- `flare_eval.py` - Evaluate flare metrics
- `flare_gen.py` - Generate synthetic data
- `flare_viz.py` - Create visualizations

#### RGB Tools
- `flare_eval_rgb.py` - Evaluate RGB flare
- `flare_gen_rgb.py` - Generate RGB data
- `flare_viz_rgb.py` - Visualize RGB flare
- `flare_convert_rgb.py` - Convert formats

#### Utility
- `flare_help.py` - Help system

## 💡 Usage Benefits

### Before Reorganization
```bash
python evaluate_flare.py test_simple.csv    # Confusing file location
python generate_data.py output.csv          # Generic name
python visualize_flare.py test.csv out.png  # Long command
```

### After Reorganization
```bash
python flare_eval.py data/gemini.csv        # Clear data location
python flare_gen.py output/test.csv         # Organized output
python flare_viz.py data/test.csv out.png   # Shorter, clearer
```

## 🎨 RGB Data Format

Supports flexible spacing in CSV cells:
```
100 100 100        # Single space
100   100   100    # Multiple spaces
100	100	100    # Tabs
100  	100    100  # Mixed spacing
```

## ✅ Advantages

1. **Clear Purpose**: Each file name immediately indicates its function
2. **Easy Navigation**: Alphabetical sorting groups related tools
3. **Clean Workspace**: Root contains only essential executables
4. **Organized Data**: Clear separation of input/output/test data
5. **Consistent Pattern**: `flare_[action]_[type].py` naming scheme
6. **RGB Distinction**: RGB tools clearly marked with suffix
7. **Professional Structure**: Industry-standard directory organization