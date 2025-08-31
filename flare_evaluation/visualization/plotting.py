"""
Advanced plotting utilities for flare analysis.
"""

import numpy as np
from typing import Dict, Any, List, Optional


class PlotGenerator:
    """Generate analytical plots for flare evaluation results."""
    
    def __init__(self):
        """Initialize the plot generator."""
        self.plot_configs = {
            'figure_size': (10, 8),
            'dpi': 100,
            'style': 'seaborn',
        }
    
    def plot_flare_distribution(self, 
                               data: np.ndarray,
                               result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create distribution plot of flare intensities.
        
        Args:
            data: Sensor data
            result: Evaluation results
            
        Returns:
            Plot data dictionary
        """
        flare_mask = result.get('flare_mask', np.zeros_like(data))
        flare_values = data[flare_mask > 0]
        
        if len(flare_values) == 0:
            return {'error': 'No flare regions detected'}
        
        # Calculate histogram
        hist, bins = np.histogram(flare_values, bins=50)
        
        return {
            'type': 'histogram',
            'data': hist.tolist(),
            'bins': bins.tolist(),
            'title': 'Flare Intensity Distribution',
            'xlabel': 'Intensity Value',
            'ylabel': 'Pixel Count',
        }
    
    def plot_radial_profile(self,
                           data: np.ndarray,
                           center_x: int,
                           center_y: int,
                           max_radius: int = 100) -> Dict[str, Any]:
        """
        Create radial profile plot from a light source.
        
        Args:
            data: Sensor data
            center_x, center_y: Light source center
            max_radius: Maximum radius to plot
            
        Returns:
            Plot data dictionary
        """
        height, width = data.shape
        radial_values = []
        distances = []
        
        for r in range(0, max_radius, 2):
            # Sample points at this radius
            angles = np.linspace(0, 2 * np.pi, max(8, r))
            values = []
            
            for angle in angles:
                x = int(center_x + r * np.cos(angle))
                y = int(center_y + r * np.sin(angle))
                
                if 0 <= x < width and 0 <= y < height:
                    values.append(data[y, x])
            
            if values:
                radial_values.append(np.mean(values))
                distances.append(r)
        
        return {
            'type': 'line',
            'x': distances,
            'y': radial_values,
            'title': 'Radial Intensity Profile',
            'xlabel': 'Distance from Center (pixels)',
            'ylabel': 'Mean Intensity',
            'log_y': True,  # Log scale for exponential decay
        }
    
    def plot_metrics_timeline(self,
                            metrics_history: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Plot metrics over time for sequence analysis.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plot data dictionary
        """
        if not metrics_history:
            return {'error': 'No metrics history available'}
        
        # Extract time series
        frames = list(range(len(metrics_history)))
        flare_values = [m.get('flare_value', 0) for m in metrics_history]
        pixel_counts = [m.get('signal_pixel_count', 0) for m in metrics_history]
        
        return {
            'type': 'multi_line',
            'data': [
                {
                    'x': frames,
                    'y': flare_values,
                    'label': 'Flare Value',
                    'y_axis': 'left',
                },
                {
                    'x': frames,
                    'y': pixel_counts,
                    'label': 'Affected Pixels',
                    'y_axis': 'right',
                },
            ],
            'title': 'Flare Metrics Over Time',
            'xlabel': 'Frame Number',
            'ylabel_left': 'Flare Value',
            'ylabel_right': 'Pixel Count',
        }
    
    def plot_quality_assessment(self,
                               metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create quality assessment visualization.
        
        Args:
            metrics: Advanced metrics from evaluation
            
        Returns:
            Plot data dictionary
        """
        quality = metrics.get('quality', {})
        
        categories = ['Severity', 'Coverage', 'Overall']
        values = [
            1 - quality.get('severity_score', 0),  # Invert for quality
            1 - quality.get('coverage_score', 0),
            quality.get('quality_index', 0),
        ]
        
        return {
            'type': 'bar',
            'categories': categories,
            'values': values,
            'title': 'Flare Quality Assessment',
            'ylabel': 'Quality Score (0-1)',
            'color_map': {
                'Severity': 'red',
                'Coverage': 'orange',
                'Overall': 'green',
            },
            'grade': quality.get('quality_grade', 'N/A'),
        }
    
    def plot_2d_heatmap(self,
                       data: np.ndarray,
                       title: str = 'Sensor Data Heatmap') -> Dict[str, Any]:
        """
        Create 2D heatmap plot data.
        
        Args:
            data: 2D sensor data
            title: Plot title
            
        Returns:
            Plot data dictionary
        """
        # Downsample if too large
        if data.shape[0] > 256:
            step = data.shape[0] // 256
            data = data[::step, ::step]
        
        return {
            'type': 'heatmap',
            'data': data.tolist(),
            'title': title,
            'xlabel': 'X Position',
            'ylabel': 'Y Position',
            'colorbar_label': 'Intensity',
            'aspect': 'equal',
        }