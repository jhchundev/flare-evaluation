"""
Data validation utilities.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional


class DataValidator:
    """Validate sensor data and configuration parameters."""
    
    @staticmethod
    def validate_sensor_data(data: np.ndarray, 
                           expected_shape: Optional[Tuple[int, int]] = None,
                           bit_depth: int = 10) -> Dict[str, Any]:
        """
        Validate sensor data array.
        
        Args:
            data: Sensor data array
            expected_shape: Expected (height, width) if specified
            bit_depth: Expected bit depth of sensor
            
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {},
        }
        
        # Check dimensions
        if len(data.shape) != 2:
            results['valid'] = False
            results['errors'].append(f"Data must be 2D, got shape {data.shape}")
        else:
            results['info']['shape'] = data.shape
            
            if expected_shape and data.shape != expected_shape:
                results['warnings'].append(
                    f"Shape {data.shape} differs from expected {expected_shape}"
                )
        
        # Check data range
        max_value = 2 ** bit_depth - 1
        min_val, max_val = data.min(), data.max()
        results['info']['range'] = (min_val, max_val)
        
        if min_val < 0:
            results['valid'] = False
            results['errors'].append(f"Negative values found: min={min_val}")
        
        if max_val > max_value:
            results['valid'] = False
            results['errors'].append(
                f"Values exceed {bit_depth}-bit range: max={max_val} > {max_value}"
            )
        
        # Check for NaN or Inf
        if np.isnan(data).any():
            results['valid'] = False
            results['errors'].append("Data contains NaN values")
        
        if np.isinf(data).any():
            results['valid'] = False
            results['errors'].append("Data contains infinite values")
        
        # Statistical checks
        results['info']['statistics'] = {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'median': float(np.median(data)),
        }
        
        # Check for suspicious patterns
        unique_ratio = len(np.unique(data)) / data.size
        if unique_ratio < 0.01:
            results['warnings'].append(
                f"Low unique value ratio ({unique_ratio:.3f}), data might be corrupted"
            )
        
        return results
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evaluation configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
        }
        
        # Required parameters
        required = ['offset', 'signal_threshold', 'light_threshold']
        for param in required:
            if param not in config:
                results['valid'] = False
                results['errors'].append(f"Missing required parameter: {param}")
        
        # Value range checks
        if 'offset' in config:
            if config['offset'] < 0:
                results['errors'].append("Offset must be non-negative")
                results['valid'] = False
            elif config['offset'] > 100:
                results['warnings'].append("Unusually high offset value")
        
        if 'signal_threshold' in config:
            if config['signal_threshold'] < 0:
                results['errors'].append("Signal threshold must be non-negative")
                results['valid'] = False
        
        if 'light_threshold' in config:
            if config['light_threshold'] <= config.get('offset', 0):
                results['errors'].append("Light threshold must be greater than offset")
                results['valid'] = False
        
        # Logical checks
        if all(k in config for k in ['signal_threshold', 'light_threshold']):
            if config['signal_threshold'] >= config['light_threshold']:
                results['errors'].append(
                    "Signal threshold must be less than light threshold"
                )
                results['valid'] = False
        
        return results
    
    @staticmethod
    def validate_results(results: Dict[str, Any]) -> bool:
        """
        Validate evaluation results for consistency.
        
        Args:
            results: Evaluation results dictionary
            
        Returns:
            True if results are valid
        """
        # Check for required fields
        required_fields = ['flare_value', 'sigma_value', 'signal_pixel_count']
        for field in required_fields:
            if field not in results:
                return False
        
        # Logical consistency checks
        if results['signal_pixel_count'] == 0 and results['flare_value'] != 0:
            return False
        
        if results['sigma_value'] < 0:
            return False
        
        return True