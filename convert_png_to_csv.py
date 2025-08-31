#!/usr/bin/env python3
"""
Convert PNG image to 10-bit CSV format for flare evaluation.
"""

import numpy as np
from PIL import Image
import sys
import os


def convert_png_to_10bit_csv(png_path: str, csv_path: str, target_size: tuple = (512, 512)):
    """
    Convert PNG image to 10-bit CSV format suitable for flare evaluation.
    
    Args:
        png_path: Path to input PNG file
        csv_path: Path to output CSV file
        target_size: Target dimensions (width, height) for the output
    """
    try:
        # Load the PNG image
        img = Image.open(png_path)
        print(f"Original image size: {img.size}, mode: {img.mode}")
        
        # Convert to grayscale if needed (using luminance weights)
        if img.mode != 'L':
            if img.mode == 'RGBA':
                # Handle alpha channel by compositing over black background
                background = Image.new('RGB', img.size, (0, 0, 0))
                background.paste(img, mask=img.split()[-1])  # Alpha channel as mask
                img = background
            img = img.convert('L')
            print("Converted to grayscale")
        
        # Resize if necessary
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            print(f"Resized to: {target_size}")
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)
        
        # Convert from 8-bit (0-255) to 10-bit (0-1023) range
        # Scale by factor of 1023/255 ≈ 4.012
        img_10bit = img_array * (1023.0 / 255.0)
        
        # Round to integers and ensure within valid range
        img_10bit = np.round(img_10bit).astype(np.uint16)
        img_10bit = np.clip(img_10bit, 0, 1023)
        
        print(f"10-bit range: {np.min(img_10bit)} - {np.max(img_10bit)}")
        print(f"Data shape: {img_10bit.shape}")
        
        # Save as CSV (no header, integers only)
        np.savetxt(csv_path, img_10bit, fmt='%d', delimiter=',')
        
        print(f"Successfully converted to: {csv_path}")
        
        # Print some statistics
        unique_values = len(np.unique(img_10bit))
        print(f"Unique intensity values: {unique_values}")
        print(f"Mean intensity: {np.mean(img_10bit):.1f}")
        print(f"Std deviation: {np.std(img_10bit):.1f}")
        
        # Check for potential light sources (bright pixels)
        light_threshold = 800  # Rough threshold for bright areas
        light_pixels = np.sum(img_10bit > light_threshold)
        print(f"Pixels above {light_threshold}: {light_pixels}")
        
        return img_10bit
        
    except Exception as e:
        print(f"Error converting PNG to CSV: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_png_to_csv.py <input.png> [output.csv]")
        sys.exit(1)
    
    png_path = sys.argv[1]
    
    if not os.path.exists(png_path):
        print(f"Error: Input file '{png_path}' not found")
        sys.exit(1)
    
    # Generate output filename if not provided
    if len(sys.argv) > 2:
        csv_path = sys.argv[2]
    else:
        base_name = os.path.splitext(os.path.basename(png_path))[0]
        csv_path = f"data/{base_name}_10bit.csv"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    print(f"Converting: {png_path} -> {csv_path}")
    convert_png_to_10bit_csv(png_path, csv_path)


if __name__ == "__main__":
    main()