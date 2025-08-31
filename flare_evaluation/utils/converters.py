"""
Data conversion utilities for different formats and bit depths.
"""

import numpy as np
from typing import Union, Tuple, Optional


class DataConverter:
    """Convert between different data formats and representations."""
    
    @staticmethod
    def convert_bit_depth(data: np.ndarray, 
                         from_bits: int, 
                         to_bits: int) -> np.ndarray:
        """
        Convert data between different bit depths.
        
        Args:
            data: Input data array
            from_bits: Source bit depth
            to_bits: Target bit depth
            
        Returns:
            Converted data array
        """
        if from_bits == to_bits:
            return data.copy()
        
        # Calculate scaling factor
        from_max = 2 ** from_bits - 1
        to_max = 2 ** to_bits - 1
        scale = to_max / from_max
        
        # Convert and clip
        converted = data * scale
        return np.clip(converted, 0, to_max)
    
    @staticmethod
    def normalize_data(data: np.ndarray, 
                      target_range: Tuple[float, float] = (0, 1)) -> np.ndarray:
        """
        Normalize data to specified range.
        
        Args:
            data: Input data array
            target_range: Target (min, max) range
            
        Returns:
            Normalized data array
        """
        min_val = data.min()
        max_val = data.max()
        
        if max_val == min_val:
            return np.full_like(data, target_range[0])
        
        # Normalize to 0-1
        normalized = (data - min_val) / (max_val - min_val)
        
        # Scale to target range
        target_min, target_max = target_range
        scaled = normalized * (target_max - target_min) + target_min
        
        return scaled
    
    @staticmethod
    def to_uint8(data: np.ndarray, 
                 clip: bool = True) -> np.ndarray:
        """
        Convert data to uint8 format (0-255).
        
        Args:
            data: Input data array
            clip: Whether to clip values to valid range
            
        Returns:
            uint8 data array
        """
        if data.dtype == np.uint8:
            return data.copy()
        
        # Determine conversion based on data range
        max_val = data.max()
        
        if max_val <= 1.0:
            # Assume normalized data
            converted = data * 255
        elif max_val <= 255:
            # Already in uint8 range
            converted = data
        elif max_val <= 1023:
            # Likely 10-bit data
            converted = data / 1023 * 255
        elif max_val <= 4095:
            # Likely 12-bit data
            converted = data / 4095 * 255
        elif max_val <= 16383:
            # Likely 14-bit data
            converted = data / 16383 * 255
        elif max_val <= 65535:
            # Likely 16-bit data
            converted = data / 65535 * 255
        else:
            # Unknown range, normalize
            converted = DataConverter.normalize_data(data, (0, 255))
        
        if clip:
            converted = np.clip(converted, 0, 255)
        
        return converted.astype(np.uint8)
    
    @staticmethod
    def to_float32(data: np.ndarray, 
                  normalize: bool = True) -> np.ndarray:
        """
        Convert data to float32 format.
        
        Args:
            data: Input data array
            normalize: Whether to normalize to 0-1 range
            
        Returns:
            float32 data array
        """
        if data.dtype == np.float32 and not normalize:
            return data.copy()
        
        converted = data.astype(np.float32)
        
        if normalize:
            converted = DataConverter.normalize_data(converted, (0, 1))
        
        return converted
    
    @staticmethod
    def rgb_to_grayscale(rgb: np.ndarray, 
                        weights: Optional[Tuple[float, float, float]] = None) -> np.ndarray:
        """
        Convert RGB image to grayscale.
        
        Args:
            rgb: RGB image array (H x W x 3)
            weights: RGB weights for conversion
            
        Returns:
            Grayscale image array (H x W)
        """
        if len(rgb.shape) == 2:
            return rgb  # Already grayscale
        
        if len(rgb.shape) != 3 or rgb.shape[2] != 3:
            raise ValueError(f"Expected RGB image with shape (H, W, 3), got {rgb.shape}")
        
        # Use standard weights if not provided
        if weights is None:
            weights = (0.299, 0.587, 0.114)  # ITU-R BT.601
        
        r, g, b = weights
        grayscale = rgb[:, :, 0] * r + rgb[:, :, 1] * g + rgb[:, :, 2] * b
        
        return grayscale
    
    @staticmethod
    def grayscale_to_rgb(gray: np.ndarray) -> np.ndarray:
        """
        Convert grayscale image to RGB.
        
        Args:
            gray: Grayscale image array (H x W)
            
        Returns:
            RGB image array (H x W x 3)
        """
        if len(gray.shape) == 3:
            return gray  # Already RGB
        
        if len(gray.shape) != 2:
            raise ValueError(f"Expected grayscale image with shape (H, W), got {gray.shape}")
        
        return np.stack([gray, gray, gray], axis=-1)