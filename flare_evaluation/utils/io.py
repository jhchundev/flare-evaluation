"""
Input/Output utilities for data handling.
"""

import csv
import numpy as np
from typing import List, Union, Optional
import json
import os


class DataLoader:
    """Load data from various file formats."""
    
    @staticmethod
    def load_csv(filepath: str) -> np.ndarray:
        """
        Load CSV file into numpy array.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            2D numpy array of data
        """
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)
            data = [list(map(float, row)) for row in reader]
        
        return np.array(data)
    
    @staticmethod
    def load_numpy(filepath: str) -> np.ndarray:
        """Load numpy .npy or .npz file."""
        if filepath.endswith('.npz'):
            data = np.load(filepath)
            return data['arr_0'] if 'arr_0' in data else data[list(data.keys())[0]]
        return np.load(filepath)
    
    @staticmethod
    def load_json(filepath: str) -> dict:
        """Load JSON configuration file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def load_batch(directory: str, pattern: str = '*.csv') -> List[np.ndarray]:
        """
        Load multiple files from directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            
        Returns:
            List of loaded data arrays
        """
        import glob
        
        files = glob.glob(os.path.join(directory, pattern))
        data_list = []
        
        for filepath in sorted(files):
            if filepath.endswith('.csv'):
                data = DataLoader.load_csv(filepath)
            elif filepath.endswith(('.npy', '.npz')):
                data = DataLoader.load_numpy(filepath)
            else:
                continue
            
            data_list.append(data)
        
        return data_list


class DataWriter:
    """Write data to various file formats."""
    
    @staticmethod
    def save_csv(data: np.ndarray, filepath: str, precision: int = 2):
        """
        Save numpy array to CSV file.
        
        Args:
            data: Data array to save
            filepath: Output file path
            precision: Decimal precision for floating point values
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in data:
                formatted_row = [f"{val:.{precision}f}" for val in row]
                writer.writerow(formatted_row)
    
    @staticmethod
    def save_numpy(data: np.ndarray, filepath: str, compressed: bool = False):
        """
        Save numpy array to .npy or .npz file.
        
        Args:
            data: Data array to save
            filepath: Output file path
            compressed: Whether to use compression
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        if compressed or filepath.endswith('.npz'):
            np.savez_compressed(filepath, data)
        else:
            np.save(filepath, data)
    
    @staticmethod
    def save_json(data: dict, filepath: str, indent: int = 2):
        """
        Save dictionary to JSON file.
        
        Args:
            data: Dictionary to save
            filepath: Output file path
            indent: JSON indentation level
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
    
    @staticmethod
    def save_results(results: dict, filepath: str):
        """
        Save evaluation results to formatted text file.
        
        Args:
            results: Evaluation results dictionary
            filepath: Output file path
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("FLARE EVALUATION RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            # Basic metrics
            f.write("Basic Metrics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Flare Value: {results.get('flare_value', 0):.4f}\n")
            f.write(f"Total Signal: {results.get('sigma_value', 0):.2f}\n")
            f.write(f"Affected Pixels: {results.get('signal_pixel_count', 0)}\n")
            f.write(f"Light Source Pixels: {results.get('light_pixel_count', 0)}\n")
            f.write(f"Coverage: {results.get('flare_coverage_percent', 0):.2f}%\n")
            
            # Additional metrics if available
            if 'mean_flare_intensity' in results:
                f.write("\nIntensity Statistics:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Mean Intensity: {results['mean_flare_intensity']:.2f}\n")
                f.write(f"Max Intensity: {results['max_flare_intensity']:.2f}\n")


class ImageWriter:
    """Write image data to various formats."""
    
    @staticmethod
    def save_pgm(data: np.ndarray, filepath: str):
        """
        Save data as PGM (Portable Gray Map) file.
        
        Args:
            data: 2D array of grayscale values (0-255)
            filepath: Output file path
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        height, width = data.shape
        
        with open(filepath, 'w') as f:
            # PGM header
            f.write('P2\n')  # ASCII grayscale
            f.write(f'{width} {height}\n')
            f.write('255\n')  # Max value
            
            # Write pixel data
            for row in data:
                f.write(' '.join(str(int(v)) for v in row) + '\n')
    
    @staticmethod
    def save_ppm(data: np.ndarray, filepath: str):
        """
        Save RGB data as PPM (Portable Pixel Map) file.
        
        Args:
            data: 3D array of RGB values (H x W x 3)
            filepath: Output file path
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        if len(data.shape) == 2:
            # Convert grayscale to RGB
            data = np.stack([data, data, data], axis=-1)
        
        height, width, channels = data.shape
        
        with open(filepath, 'w') as f:
            # PPM header
            f.write('P3\n')  # ASCII RGB
            f.write(f'{width} {height}\n')
            f.write('255\n')  # Max value
            
            # Write pixel data
            for row in data:
                for pixel in row:
                    f.write(f'{int(pixel[0])} {int(pixel[1])} {int(pixel[2])} ')
                f.write('\n')
    
    @staticmethod
    def save_image(data: np.ndarray, filepath: str, format: str = 'png', **kwargs):
        """
        Save image using PIL with advanced options.
        
        Args:
            data: Image data array
            filepath: Output file path
            format: Image format ('png', 'jpg', 'tiff', etc.)
            **kwargs: Additional save parameters (quality, dpi, compression, etc.)
        """
        try:
            from PIL import Image
            
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            # Ensure uint8 data type
            if data.dtype != np.uint8:
                data = np.clip(data, 0, 255).astype(np.uint8)
            
            # Handle different array shapes
            if len(data.shape) == 2:
                # Grayscale
                img = Image.fromarray(data, mode='L')
            elif len(data.shape) == 3 and data.shape[2] == 3:
                # RGB
                img = Image.fromarray(data, mode='RGB')
            elif len(data.shape) == 3 and data.shape[2] == 4:
                # RGBA
                img = Image.fromarray(data, mode='RGBA')
            else:
                raise ValueError(f"Unsupported array shape: {data.shape}")
            
            # Apply format-specific options
            save_kwargs = {}
            
            if format.lower() == 'png':
                save_kwargs['compress_level'] = kwargs.get('compress_level', 6)
                save_kwargs['optimize'] = kwargs.get('optimize', True)
                if 'dpi' in kwargs:
                    save_kwargs['dpi'] = (kwargs['dpi'], kwargs['dpi'])
            elif format.lower() in ['jpg', 'jpeg']:
                save_kwargs['quality'] = kwargs.get('quality', 95)
                save_kwargs['optimize'] = kwargs.get('optimize', True)
                if 'dpi' in kwargs:
                    save_kwargs['dpi'] = (kwargs['dpi'], kwargs['dpi'])
            elif format.lower() == 'tiff':
                save_kwargs['compression'] = kwargs.get('compression', 'tiff_lzw')
                if 'dpi' in kwargs:
                    save_kwargs['dpi'] = (kwargs['dpi'], kwargs['dpi'])
            
            # Save with appropriate parameters
            img.save(filepath, format=format.upper(), **save_kwargs)
            
        except ImportError:
            # Fall back to PGM/PPM
            print("Warning: Pillow not installed, falling back to PGM/PPM format")
            if len(data.shape) == 2:
                ImageWriter.save_pgm(data, filepath.replace(f'.{format}', '.pgm'))
            else:
                ImageWriter.save_ppm(data, filepath.replace(f'.{format}', '.ppm'))
    
    @staticmethod
    def save_png(data: np.ndarray, filepath: str, 
                 compress_level: int = 6, 
                 optimize: bool = True,
                 dpi: Optional[int] = None):
        """
        Save data as PNG with specific options.
        
        Args:
            data: Image data array
            filepath: Output file path
            compress_level: PNG compression level (0-9)
            optimize: Whether to optimize the PNG
            dpi: Dots per inch for the image
        """
        ImageWriter.save_image(
            data, filepath, 'png',
            compress_level=compress_level,
            optimize=optimize,
            dpi=dpi
        )
    
    @staticmethod
    def save_with_colormap(data: np.ndarray, filepath: str, 
                          colormap: str = 'viridis',
                          format: str = 'png'):
        """
        Save grayscale data with a colormap applied.
        
        Args:
            data: 2D grayscale data array
            filepath: Output file path
            colormap: Colormap name ('viridis', 'jet', 'hot', 'cool', etc.)
            format: Output format
        """
        try:
            from PIL import Image
            import numpy as np
            
            # Normalize to 0-255
            if data.dtype != np.uint8:
                min_val = data.min()
                max_val = data.max()
                if max_val > min_val:
                    normalized = (data - min_val) / (max_val - min_val) * 255
                else:
                    normalized = np.zeros_like(data)
                data = normalized.astype(np.uint8)
            
            # Apply colormap
            if colormap == 'viridis':
                # Viridis colormap approximation
                r = np.clip(data * 0.3 + 50, 0, 255)
                g = np.clip(data * 0.8 + 20, 0, 255)
                b = np.clip(255 - data * 0.5, 0, 255)
            elif colormap == 'jet':
                # Jet colormap approximation
                r = np.clip(4 * data - 510, 0, 255)
                g = np.clip(510 - np.abs(4 * data - 510), 0, 255)
                b = np.clip(510 - 4 * data, 0, 255)
            elif colormap == 'hot':
                # Hot colormap approximation
                r = np.clip(data * 3, 0, 255)
                g = np.clip(data * 3 - 255, 0, 255)
                b = np.clip(data * 3 - 510, 0, 255)
            elif colormap == 'cool':
                # Cool colormap approximation
                r = data
                g = 255 - data
                b = 255
            elif colormap == 'gray' or colormap == 'grey':
                # Grayscale
                r = g = b = data
            else:
                # Default to grayscale
                r = g = b = data
            
            # Stack into RGB
            rgb = np.stack([r.astype(np.uint8), 
                          g.astype(np.uint8), 
                          b.astype(np.uint8)], axis=-1)
            
            # Save
            ImageWriter.save_image(rgb, filepath, format)
            
        except ImportError:
            print("Warning: Pillow not installed, saving as grayscale PGM")
            ImageWriter.save_pgm(data, filepath.replace(f'.{format}', '.pgm'))