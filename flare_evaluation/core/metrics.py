"""
Advanced metrics calculation for flare evaluation.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import ndimage
import warnings

# Suppress scipy import warning if not available
try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available, some advanced metrics will be disabled")


class FlareMetrics:
    """Calculate advanced metrics for flare analysis."""
    
    def compute_advanced_metrics(self, result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute advanced metrics from evaluation results.
        
        Args:
            result: Basic evaluation results
            config: Evaluator configuration
            
        Returns:
            Dictionary of advanced metrics
        """
        metrics = {
            'basic': self._extract_basic_metrics(result),
            'statistical': self._compute_statistical_metrics(result),
            'spatial': self._compute_spatial_metrics(result),
            'quality': self._compute_quality_metrics(result, config),
        }
        
        return metrics
    
    def _extract_basic_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format basic metrics."""
        return {
            'flare_value': result['flare_value'],
            'total_signal': result['sigma_value'],
            'affected_pixels': result['signal_pixel_count'],
            'light_sources': result['light_pixel_count'],
            'coverage_percent': result['flare_coverage_percent'],
        }
    
    def _compute_statistical_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Compute statistical metrics of flare distribution."""
        return {
            'mean_intensity': result['mean_flare_intensity'],
            'max_intensity': result['max_flare_intensity'],
            'intensity_ratio': (
                result['mean_flare_intensity'] / result['max_flare_intensity']
                if result['max_flare_intensity'] > 0 else 0
            ),
        }
    
    def _compute_spatial_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Compute spatial distribution metrics."""
        flare_mask = result['flare_mask']
        
        if not SCIPY_AVAILABLE:
            return {'available': False}
        
        # Find connected components
        labeled_array, num_features = ndimage.label(flare_mask > 0)
        
        # Compute centroids and sizes of flare regions
        if num_features > 0:
            sizes = ndimage.sum(flare_mask > 0, labeled_array, range(1, num_features + 1))
            max_region_size = np.max(sizes) if len(sizes) > 0 else 0
            mean_region_size = np.mean(sizes) if len(sizes) > 0 else 0
        else:
            max_region_size = 0
            mean_region_size = 0
        
        return {
            'num_flare_regions': num_features,
            'max_region_size': max_region_size,
            'mean_region_size': mean_region_size,
            'spatial_distribution': self._calculate_distribution_score(flare_mask),
        }
    
    def _compute_quality_metrics(self, result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Compute quality assessment metrics."""
        flare_value = result['flare_value']
        max_possible = config.get('max_value', 1023) - config.get('offset', 64)
        
        # Quality scores based on flare characteristics
        severity_score = min(flare_value / 100, 1.0)  # Normalized to 0-1
        coverage_score = result['flare_coverage_percent'] / 100
        
        # Overall quality assessment
        quality_index = 1.0 - (severity_score * 0.6 + coverage_score * 0.4)
        
        return {
            'severity_score': severity_score,
            'coverage_score': coverage_score,
            'quality_index': quality_index,
            'quality_grade': self._get_quality_grade(quality_index),
        }
    
    def _calculate_distribution_score(self, mask: np.ndarray) -> float:
        """
        Calculate spatial distribution score (0-1).
        Higher scores indicate more concentrated flare.
        """
        if not SCIPY_AVAILABLE or np.sum(mask) == 0:
            return 0.0
        
        # Calculate center of mass
        com = ndimage.center_of_mass(mask)
        
        # Calculate spread from center
        y_indices, x_indices = np.where(mask > 0)
        if len(y_indices) == 0:
            return 0.0
        
        distances = np.sqrt((y_indices - com[0])**2 + (x_indices - com[1])**2)
        mean_distance = np.mean(distances)
        max_distance = np.sqrt(mask.shape[0]**2 + mask.shape[1]**2) / 2
        
        # Normalize (inverse so concentrated = higher score)
        return 1.0 - (mean_distance / max_distance)
    
    def _get_quality_grade(self, quality_index: float) -> str:
        """Convert quality index to letter grade."""
        if quality_index >= 0.9:
            return 'A'
        elif quality_index >= 0.8:
            return 'B'
        elif quality_index >= 0.7:
            return 'C'
        elif quality_index >= 0.6:
            return 'D'
        else:
            return 'F'