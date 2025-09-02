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
            'offset': 64,                     # Sensor black level (ADU)
            'signal_threshold': 10,           # Minimum signal above offset (ADU)
            'direct_illumination_threshold': 400,  # Direct illumination threshold (ADU)
            'light_threshold': 600,           # Light source core threshold (ADU)
            'pixel_pitch_um': 2.4,           # Pixel pitch in micrometers (typical smartphone)
            'beta_coverage': 0.5,            # Coverage penalty exponent for F_final
            'bit_depth': 10,                # Sensor bit depth
            'max_value': 1023,              # Maximum sensor value (2^10 - 1)
            # Legacy parameters (deprecated)
            'pixel_size': None,              # Deprecated - use pixel_pitch_um
            'light_amount': None,            # Deprecated - use F_norm instead
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
        pixel_pitch_um = self.config.get('pixel_pitch_um', 2.4)
        beta_coverage = self.config.get('beta_coverage', 0.5)
        
        # Handle legacy parameters with warning
        if 'pixel_size' in self.config and self.config['pixel_size'] is not None:
            import warnings
            warnings.warn("pixel_size is deprecated. Use pixel_pitch_um instead.", DeprecationWarning)
            # Assume pixel_size was in arbitrary units, keep pixel_pitch_um default
        
        # Calculate pixel area in square micrometers
        pixel_area_um2 = pixel_pitch_um ** 2
        
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
        N_sensor = data.size
        
        # === METRIC 1: Raw Flare Intensity (F_raw) ===
        # Average flare signal per unit physical area
        F_raw = 0.0
        if signal_pixel_count > 0:
            F_raw = sigma_value / (signal_pixel_count * pixel_area_um2)
        
        # === METRIC 2: Area-Normalized Flare Ratio (F_norm) ===
        # Dimensionless ratio against direct illumination
        F_norm = 0.0
        direct_pixels_values = data[direct_illumination_mask] - offset
        if signal_pixel_count > 0 and len(direct_pixels_values) > 0:
            flare_intensity = sigma_value / (signal_pixel_count * pixel_area_um2)
            direct_intensity = np.sum(direct_pixels_values) / (len(direct_pixels_values) * pixel_area_um2)
            if direct_intensity > 0:
                F_norm = flare_intensity / direct_intensity
        elif signal_pixel_count > 0 and light_pixels > 0:
            # Fallback: use light source as reference
            light_pixels_values = data[light_mask] - offset
            flare_intensity = sigma_value / (signal_pixel_count * pixel_area_um2)
            light_intensity = np.sum(light_pixels_values) / (len(light_pixels_values) * pixel_area_um2)
            if light_intensity > 0:
                F_norm = flare_intensity / light_intensity
        
        # === METRIC 3: Coverage-Weighted Flare Index (F_final) ===
        # Adds spatial coverage penalty
        coverage_ratio = signal_pixel_count / N_sensor if N_sensor > 0 else 0
        coverage_weight = coverage_ratio ** beta_coverage
        F_final = F_norm * coverage_weight
        
        # Legacy flare value for backward compatibility
        # (Deprecated - will be removed in future versions)
        flare_value = F_raw * pixel_area_um2  # Convert back to legacy units
        
        # Additional metrics
        mean_flare_intensity = np.mean(flare_pixels) if len(flare_pixels) > 0 else 0
        max_flare_intensity = np.max(flare_pixels) if len(flare_pixels) > 0 else 0
        flare_coverage = signal_pixel_count / data.size * 100  # Percentage
        
        # Store results (with new direct illumination metrics)
        direct_illumination_coverage = direct_illumination_pixels / data.size * 100
        
        self._last_result = {
            # New resolution-independent metrics
            'F_raw': F_raw,                      # Raw flare intensity (ADU/µm²)
            'F_norm': F_norm,                    # Normalized flare ratio (dimensionless)
            'F_final': F_final,                  # Coverage-weighted index (dimensionless)
            
            # Physical parameters
            'pixel_pitch_um': pixel_pitch_um,
            'pixel_area_um2': pixel_area_um2,
            
            # Legacy metrics (deprecated)
            'flare_value': flare_value,          # Legacy value (deprecated)
            'sigma_value': sigma_value,
            
            # Pixel counts
            'signal_pixel_count': signal_pixel_count,
            'light_pixel_count': light_pixels,
            'direct_illumination_pixel_count': direct_illumination_pixels,
            
            # Statistics
            'mean_flare_intensity': mean_flare_intensity,
            'max_flare_intensity': max_flare_intensity,
            'flare_coverage_percent': flare_coverage,
            'direct_illumination_coverage_percent': direct_illumination_coverage,
            'coverage_ratio': coverage_ratio,
            'coverage_weight': coverage_weight,
            
            # Masks for visualization
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