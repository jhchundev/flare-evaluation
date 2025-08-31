"""
Core flare evaluation engine with advanced analysis capabilities.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..utils.io import DataLoader
from .metrics import FlareMetrics


class FlareEvaluator:
    """
    Advanced flare evaluation system for optical sensor data analysis.
    
    This evaluator implements sophisticated algorithms for detecting and
    quantifying optical flare in sensor arrays, particularly optimized
    for 10-bit sensor systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the flare evaluator with configuration.
        
        Args:
            config: Configuration dictionary with evaluation parameters
        """
        self.config = config or self._default_config()
        self.metrics_calculator = FlareMetrics()
        self.data_loader = DataLoader()
        self._last_result = None
        
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Return default configuration parameters."""
        return {
            'offset': 64,                     # Sensor black level
            'signal_threshold': 10,           # Minimum signal above offset
            'direct_illumination_threshold': 400,  # Direct illumination threshold (new)
            'light_threshold': 600,           # Light source core threshold (increased)
            'pixel_size': 1.0,               # Physical pixel size
            'light_amount': 1.0,             # Light normalization factor
            'bit_depth': 10,                # Sensor bit depth
            'max_value': 1023,              # Maximum sensor value (2^10 - 1)
        }
    
    def evaluate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Perform comprehensive flare evaluation on sensor data.
        
        Args:
            data: 2D numpy array of sensor readings
            
        Returns:
            Dictionary containing evaluation results and metrics
        """
        # Extract configuration with defaults
        offset = self.config.get('offset', 64)
        signal_threshold = self.config.get('signal_threshold', 10)
        direct_illumination_threshold = self.config.get('direct_illumination_threshold', 400)
        light_threshold = self.config.get('light_threshold', 600)
        pixel_size = self.config.get('pixel_size', 1.0)
        light_amount = self.config.get('light_amount', 1.0)
        
        # Identify light source cores (very bright pixels)
        light_mask = data > light_threshold
        light_pixels = np.sum(light_mask)
        
        # Identify direct illumination regions (bright but not core)
        direct_illumination_mask = (
            (data > direct_illumination_threshold) & 
            (data <= light_threshold)
        )
        direct_illumination_pixels = np.sum(direct_illumination_mask)
        
        # Detect flare-affected regions (improved algorithm)
        flare_condition = (
            (data > offset + signal_threshold) & 
            (data <= direct_illumination_threshold)  # Key change: stop at direct_illumination_threshold
        )
        flare_mask = flare_condition.astype(np.uint8) * 255
        
        # Calculate flare metrics
        flare_pixels = data[flare_condition] - offset
        sigma_value = np.sum(flare_pixels)
        signal_pixel_count = len(flare_pixels)
        pixel_area = pixel_size * pixel_size
        
        # Compute flare value
        if signal_pixel_count > 0 and pixel_area > 0:
            flare_value = sigma_value / (signal_pixel_count * pixel_area) * light_amount
        else:
            flare_value = 0.0
        
        # Additional metrics
        mean_flare_intensity = np.mean(flare_pixels) if len(flare_pixels) > 0 else 0
        max_flare_intensity = np.max(flare_pixels) if len(flare_pixels) > 0 else 0
        flare_coverage = signal_pixel_count / data.size * 100  # Percentage
        
        # Store results (with new direct illumination metrics)
        direct_illumination_coverage = direct_illumination_pixels / data.size * 100
        
        self._last_result = {
            'flare_value': flare_value,
            'sigma_value': sigma_value,
            'signal_pixel_count': signal_pixel_count,
            'light_pixel_count': light_pixels,
            'direct_illumination_pixel_count': direct_illumination_pixels,
            'mean_flare_intensity': mean_flare_intensity,
            'max_flare_intensity': max_flare_intensity,
            'flare_coverage_percent': flare_coverage,
            'direct_illumination_coverage_percent': direct_illumination_coverage,
            'flare_mask': flare_mask,
            'light_mask': light_mask,
            'direct_illumination_mask': direct_illumination_mask,
        }
        
        return self._last_result
    
    def evaluate_file(self, filepath: str) -> Dict[str, Any]:
        """
        Evaluate flare from a CSV file.
        
        Args:
            filepath: Path to CSV file containing sensor data
            
        Returns:
            Dictionary containing evaluation results
        """
        data = self.data_loader.load_csv(filepath)
        return self.evaluate(data)
    
    def get_detailed_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed metrics from the last evaluation.
        
        Returns:
            Detailed metrics dictionary or None if no evaluation performed
        """
        if self._last_result is None:
            return None
            
        return self.metrics_calculator.compute_advanced_metrics(
            self._last_result,
            self.config
        )
    
    def update_config(self, **kwargs):
        """
        Update evaluator configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self.config.update(kwargs)