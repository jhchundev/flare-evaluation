import csv
import argparse
from typing import List, Tuple


def read_csv(path: str) -> List[List[float]]:
    """Read CSV file into a 2D list of floats."""
    with open(path, newline='') as f:
        reader = csv.reader(f)
        return [list(map(float, row)) for row in reader]

def compute_flare(
    data: List[List[float]],
    offset: float = 64,
    signal_threshold: float = 0,
    light_threshold: float = 255,
    pixel_size: float = 1.0,
    light_amount: float = 1.0,
) -> Tuple[float, float, int, List[List[int]]]:
    """Compute flare metric and return target mask."""
    target_mask: List[List[int]] = []
    signal_values: List[float] = []
    for row in data:
        mask_row: List[int] = []
        for value in row:
            if value > (offset + signal_threshold) and value < light_threshold:
                signal_values.append(value - offset)
                mask_row.append(255)
            else:
                mask_row.append(0)
        target_mask.append(mask_row)
    sigma_value = sum(signal_values)
    signal_pixel_number = len(signal_values)
    pixel_area = pixel_size * pixel_size
    flare_value = 0.0
    if signal_pixel_number > 0 and pixel_area > 0:
        flare_value = sigma_value / (signal_pixel_number * pixel_area) * light_amount
    return flare_value, sigma_value, signal_pixel_number, target_mask

def save_mask_as_pgm(mask: List[List[int]], path: str) -> None:
    height = len(mask)
    width = len(mask[0]) if height else 0
    with open(path, 'w') as f:
        f.write('P2\n')
        f.write(f'{width} {height}\n')
        f.write('255\n')
        for row in mask:
            f.write(' '.join(str(v) for v in row) + '\n')

def main() -> None:
    parser = argparse.ArgumentParser(description='Compute flare metric from sensor data CSV.')
    parser.add_argument('csv_path', help='Path to 512x512 CSV file')
    parser.add_argument('--offset', type=float, default=64, help='Sensor offset (black level)')
    parser.add_argument('--signal-threshold', type=float, default=10, help='Threshold above offset for flare')
    parser.add_argument('--light-threshold', type=float, default=250, help='Pixel value threshold to exclude light source')
    parser.add_argument('--pixel-size', type=float, default=1.0, help='Pixel size for area calculation')
    parser.add_argument('--light-amount', type=float, default=1.0, help='Amount of light used for normalization')
    parser.add_argument('--plot', type=str, default='target_region.pgm', help='Path to save PGM plot of target region')
    args = parser.parse_args()

    data = read_csv(args.csv_path)
    flare, sigma, num, mask = compute_flare(
        data,
        offset=args.offset,
        signal_threshold=args.signal_threshold,
        light_threshold=args.light_threshold,
        pixel_size=args.pixel_size,
        light_amount=args.light_amount,
    )
    save_mask_as_pgm(mask, args.plot)

    print(f'Sum of target pixel values: {sigma}')
    print(f'Signal pixel number: {num}')
    print(f'Flare value: {flare}')

if __name__ == '__main__':
    main()
