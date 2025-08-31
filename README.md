# Flare Evaluation

This project provides a simple tool to evaluate image sensor flare from a 512x512 CSV file.

## Usage

1. Prepare a CSV file containing 512x512 pixel values (see `sample_data.csv` for an example).
2. Run the evaluator:

```bash
python flare_evaluator.py your_data.csv --signal-threshold 10 --light-threshold 200 --pixel-size 1.0 --light-amount 100 --plot result.pgm
```

### Parameters
- `offset`: Sensor black level (default: 64)
- `signal-threshold`: Minimum value above offset to consider a pixel as flare (default: 10)
- `light-threshold`: Pixel values above this are treated as light source and excluded (default: 250)
- `pixel-size`: Physical size of one pixel (default: 1.0)
- `light-amount`: Amount of light for normalization (default: 1.0)
- `plot`: Output PGM file showing the 2D target region

The script prints the sum of target pixel values, the number of signal pixels, and the final flare value.
