#!/usr/bin/env python3
"""Bulk processing utility for Flare Evaluation System.

Iterates through all CSV files in a directory and evaluates each using the
current CONFIG settings. Results are written to the output directory with the
same base filename as the input.
"""

from pathlib import Path
import argparse

from config import CONFIG
from flare import process_grayscale, process_rgb

def bulk_process(input_dir: Path, output_dir: Path) -> None:
    mode = CONFIG.get('mode', 'grayscale')
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for csv_file in sorted(input_dir.glob('*.csv')):
        stem = csv_file.stem
        json_path = output_dir / f"{stem}.json"
        png_path = output_dir / f"{stem}.png"
        print(f"\n=== Processing {csv_file} ===")
        if mode == 'rgb':
            process_rgb(csv_file, output_json=json_path, output_image=png_path)
        else:
            process_grayscale(csv_file, output_json=json_path, output_image=png_path)


def main():
    parser = argparse.ArgumentParser(description="Bulk process CSV files for flare evaluation")
    parser.add_argument('input_dir', nargs='?', default='data', help='Directory containing CSV files')
    parser.add_argument('output_dir', nargs='?', default='output', help='Directory to save outputs')
    args = parser.parse_args()

    bulk_process(Path(args.input_dir), Path(args.output_dir))

if __name__ == '__main__':
    main()
