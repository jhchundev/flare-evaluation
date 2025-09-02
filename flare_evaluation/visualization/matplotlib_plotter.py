"""
Matplotlib-based plotting utilities for flare analysis visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Dict, Any, List, Optional, Tuple, Union
import warnings


class MatplotlibPlotter:
    """
    Matplotlib-based plotter for flare evaluation results.
    
    Provides comprehensive plotting capabilities including heatmaps,
    distributions, radial profiles, and quality assessments.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (10, 8), dpi: int = 100):
        """
        Initialize the matplotlib plotter.
        
        Args:
            style: Matplotlib style to use
            figsize: Default figure size
            dpi: Dots per inch for figure resolution
        """
        self.figsize = figsize
        self.dpi = dpi
        
        # Try to set style, fallback to default if not available
        try:
            plt.style.use(style)
        except:
            warnings.warn(f"Style '{style}' not available, using default")
    
    def plot_flare_heatmap(self, 
                          data: np.ndarray,
                          evaluation_result: Optional[Dict[str, Any]] = None,
                          title: str = "Flare Analysis Heatmap",
                          colormap: str = 'viridis',
                          save_path: Optional[str] = None,
                          show: bool = True) -> Figure:
        """
        Create a heatmap visualization of sensor data with flare overlays.
        
        Args:
            data: 2D sensor data array
            evaluation_result: Optional evaluation results for overlays
            title: Plot title
            colormap: Colormap to use for data visualization
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Plot base heatmap
        im = ax.imshow(data, cmap=colormap, aspect='equal')
        plt.colorbar(im, ax=ax, label='Intensity')
        
        # Add overlays if evaluation results provided
        if evaluation_result:
            # Overlay flare regions
            if 'flare_mask' in evaluation_result:
                flare_mask = evaluation_result['flare_mask']
                # Create transparent overlay for flare regions
                overlay = np.ma.masked_where(flare_mask == 0, flare_mask)
                ax.imshow(overlay, cmap='Reds', alpha=0.3, aspect='equal')
            
            # Add light source markers
            if 'light_sources' in evaluation_result:
                for source in evaluation_result['light_sources']:
                    circle = plt.Circle((source['x'], source['y']), 
                                       source.get('radius', 10), 
                                       color='yellow', fill=False, linewidth=2)
                    ax.add_patch(circle)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position (pixels)')
        ax.set_ylabel('Y Position (pixels)')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_intensity_distribution(self,
                                  data: np.ndarray,
                                  evaluation_result: Optional[Dict[str, Any]] = None,
                                  bins: int = 50,
                                  log_scale: bool = True,
                                  save_path: Optional[str] = None,
                                  show: bool = True) -> Figure:
        """
        Plot histogram of intensity values with region classification.
        
        Args:
            data: Sensor data array
            evaluation_result: Optional evaluation results
            bins: Number of histogram bins
            log_scale: Whether to use log scale for y-axis
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Flatten data for histogram
        flat_data = data.flatten()
        
        # Plot overall distribution
        n, bins_edges, patches = ax.hist(flat_data, bins=bins, alpha=0.7, 
                                         color='blue', label='All pixels', 
                                         edgecolor='black')
        
        # Overlay flare region distribution if available
        if evaluation_result and 'flare_mask' in evaluation_result:
            flare_mask = evaluation_result['flare_mask']
            flare_values = data[flare_mask > 0]
            if len(flare_values) > 0:
                ax.hist(flare_values, bins=bins_edges, alpha=0.5, 
                       color='red', label='Flare regions', edgecolor='darkred')
        
        # Add threshold lines if config available
        if evaluation_result and 'config' in evaluation_result:
            config = evaluation_result['config']
            offset = config.get('offset', 0)
            signal_threshold = config.get('signal_threshold', 0)
            light_threshold = config.get('light_threshold', 1023)
            
            ax.axvline(offset + signal_threshold, color='green', linestyle='--', 
                      label=f'Signal threshold ({offset + signal_threshold})')
            ax.axvline(light_threshold, color='orange', linestyle='--', 
                      label=f'Light threshold ({light_threshold})')
        
        ax.set_xlabel('Intensity Value', fontsize=12)
        ax.set_ylabel('Pixel Count' + (' (log scale)' if log_scale else ''), fontsize=12)
        ax.set_title('Intensity Distribution Analysis', fontsize=14, fontweight='bold')
        
        if log_scale:
            ax.set_yscale('log')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_radial_profile(self,
                          data: np.ndarray,
                          center: Tuple[int, int],
                          max_radius: Optional[int] = None,
                          angle_samples: int = 36,
                          save_path: Optional[str] = None,
                          show: bool = True) -> Figure:
        """
        Plot radial intensity profile from a center point.
        
        Args:
            data: Sensor data array
            center: (x, y) coordinates of center point
            max_radius: Maximum radius to analyze
            angle_samples: Number of angular samples per radius
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        height, width = data.shape
        center_x, center_y = center
        
        if max_radius is None:
            max_radius = min(center_x, center_y, width - center_x, height - center_y)
        
        # Calculate radial profile
        radii = np.arange(0, max_radius, 1)
        mean_intensities = []
        std_intensities = []
        
        for r in radii:
            if r == 0:
                mean_intensities.append(data[center_y, center_x])
                std_intensities.append(0)
            else:
                angles = np.linspace(0, 2 * np.pi, angle_samples, endpoint=False)
                values = []
                for angle in angles:
                    x = int(center_x + r * np.cos(angle))
                    y = int(center_y + r * np.sin(angle))
                    if 0 <= x < width and 0 <= y < height:
                        values.append(data[y, x])
                
                if values:
                    mean_intensities.append(np.mean(values))
                    std_intensities.append(np.std(values))
                else:
                    mean_intensities.append(0)
                    std_intensities.append(0)
        
        mean_intensities = np.array(mean_intensities)
        std_intensities = np.array(std_intensities)
        
        # Create plot with dual y-axis
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, dpi=self.dpi, 
                                       sharex=True, height_ratios=[3, 1])
        
        # Main plot - radial profile
        ax1.plot(radii, mean_intensities, 'b-', linewidth=2, label='Mean intensity')
        ax1.fill_between(radii, 
                         mean_intensities - std_intensities,
                         mean_intensities + std_intensities,
                         alpha=0.3, color='blue', label='±1 std dev')
        
        ax1.set_ylabel('Intensity', fontsize=12)
        ax1.set_title(f'Radial Profile from ({center_x}, {center_y})', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_yscale('log')
        
        # Derivative plot - rate of change
        if len(radii) > 1:
            gradient = np.gradient(mean_intensities)
            ax2.plot(radii, gradient, 'r-', linewidth=1)
            ax2.set_xlabel('Distance from center (pixels)', fontsize=12)
            ax2.set_ylabel('Gradient', fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_quality_metrics(self,
                           metrics: Dict[str, Any],
                           save_path: Optional[str] = None,
                           show: bool = True) -> Figure:
        """
        Create a comprehensive quality metrics visualization.
        
        Args:
            metrics: Dictionary containing quality metrics
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        fig = plt.figure(figsize=(12, 8), dpi=self.dpi)
        
        # Create grid for subplots
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Quality grade display (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        quality = metrics.get('quality', {})
        grade = quality.get('quality_grade', 'N/A')
        grade_color = self._get_grade_color(grade)
        
        ax1.text(0.5, 0.5, grade, fontsize=72, fontweight='bold',
                ha='center', va='center', color=grade_color,
                transform=ax1.transAxes)
        ax1.set_title('Quality Grade', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. Metrics bar chart (top-middle)
        ax2 = fig.add_subplot(gs[0, 1])
        metric_names = ['Severity', 'Coverage', 'Distribution']
        metric_values = [
            1 - quality.get('severity_score', 0),
            1 - quality.get('coverage_score', 0),
            quality.get('distribution_uniformity', 0.5)
        ]
        
        bars = ax2.bar(metric_names, metric_values, color=['red', 'orange', 'blue'])
        ax2.set_ylim(0, 1)
        ax2.set_ylabel('Score (0-1)', fontsize=12)
        ax2.set_title('Quality Components', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}', ha='center', va='bottom')
        
        # 3. Flare statistics (top-right)
        ax3 = fig.add_subplot(gs[0, 2])
        stats_text = f"""
        Flare Value: {metrics.get('flare_value', 0):.2f}
        Signal Pixels: {metrics.get('signal_pixel_count', 0):,}
        Total Signal: {metrics.get('sigma_value', 0):.0f}
        Coverage: {quality.get('coverage_percentage', 0):.1f}%
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=11, 
                transform=ax3.transAxes, verticalalignment='center')
        ax3.set_title('Flare Statistics', fontsize=14, fontweight='bold')
        ax3.axis('off')
        
        # 4. Spatial distribution (bottom-left)
        ax4 = fig.add_subplot(gs[1, 0])
        spatial = quality.get('spatial_distribution', {})
        if spatial:
            quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
            quadrant_values = [spatial.get(f'quadrant_{i+1}', 0) for i in range(4)]
            ax4.bar(quadrants, quadrant_values, color='green', alpha=0.7)
            ax4.set_ylabel('Pixel Count', fontsize=12)
            ax4.set_title('Spatial Distribution', fontsize=14, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'No spatial data', ha='center', va='center',
                    transform=ax4.transAxes)
            ax4.axis('off')
        
        # 5. Intensity ranges (bottom-middle)
        ax5 = fig.add_subplot(gs[1, 1])
        intensity = quality.get('intensity_ranges', {})
        if intensity:
            ranges = list(intensity.keys())
            counts = list(intensity.values())
            ax5.barh(ranges, counts, color='purple', alpha=0.7)
            ax5.set_xlabel('Pixel Count', fontsize=12)
            ax5.set_title('Intensity Ranges', fontsize=14, fontweight='bold')
        else:
            ax5.text(0.5, 0.5, 'No intensity data', ha='center', va='center',
                    transform=ax5.transAxes)
            ax5.axis('off')
        
        # 6. Overall quality index (bottom-right)
        ax6 = fig.add_subplot(gs[1, 2])
        quality_index = quality.get('quality_index', 0)
        
        # Create a gauge-like visualization
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Color gradient for gauge
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(theta)))
        for i in range(len(theta)-1):
            ax6.fill_between([x[i], x[i+1]], [y[i], y[i+1]], 0, 
                           color=colors[i], alpha=0.8)
        
        # Add needle
        needle_angle = np.pi * (1 - quality_index)
        ax6.arrow(0, 0, 0.8 * np.cos(needle_angle), 0.8 * np.sin(needle_angle),
                 head_width=0.1, head_length=0.1, fc='black', ec='black', linewidth=2)
        
        ax6.text(0, -0.3, f'{quality_index:.2f}', fontsize=20, fontweight='bold',
                ha='center')
        ax6.set_xlim(-1.2, 1.2)
        ax6.set_ylim(-0.5, 1.2)
        ax6.set_title('Quality Index', fontsize=14, fontweight='bold')
        ax6.axis('off')
        
        plt.suptitle('Flare Evaluation Quality Report', fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_multi_frame_comparison(self,
                                  frames_data: List[Dict[str, Any]],
                                  save_path: Optional[str] = None,
                                  show: bool = True) -> Figure:
        """
        Create a multi-frame comparison plot for sequential data.
        
        Args:
            frames_data: List of dictionaries with 'data' and 'metrics' for each frame
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        n_frames = len(frames_data)
        if n_frames == 0:
            raise ValueError("No frames provided for comparison")
        
        # Determine grid layout
        cols = min(4, n_frames)
        rows = (n_frames + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3), dpi=self.dpi)
        
        if n_frames == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        # Plot each frame
        for i, frame_data in enumerate(frames_data):
            ax = axes[i]
            data = frame_data.get('data')
            metrics = frame_data.get('metrics', {})
            
            if data is not None:
                im = ax.imshow(data, cmap='viridis', aspect='equal')
                
                # Add frame info
                title = f"Frame {i+1}"
                if 'flare_value' in metrics:
                    title += f"\nFlare: {metrics['flare_value']:.2f}"
                
                ax.set_title(title, fontsize=10)
                ax.axis('off')
        
        # Hide unused subplots
        for i in range(n_frames, len(axes)):
            axes[i].axis('off')
        
        plt.suptitle('Multi-Frame Flare Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_3d_surface(self,
                       data: np.ndarray,
                       downsample: int = 4,
                       colormap: str = 'viridis',
                       save_path: Optional[str] = None,
                       show: bool = True) -> Figure:
        """
        Create a 3D surface plot of the sensor data.
        
        Args:
            data: 2D sensor data array
            downsample: Factor to downsample data for performance
            colormap: Colormap for surface
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            Matplotlib figure object
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # Downsample for performance
        data_downsampled = data[::downsample, ::downsample]
        
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # Create mesh
        X = np.arange(0, data_downsampled.shape[1])
        Y = np.arange(0, data_downsampled.shape[0])
        X, Y = np.meshgrid(X, Y)
        
        # Plot surface
        surf = ax.plot_surface(X, Y, data_downsampled, cmap=colormap,
                              linewidth=0, antialiased=True, alpha=0.9)
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Intensity')
        
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_zlabel('Intensity')
        ax.set_title('3D Intensity Surface', fontsize=14, fontweight='bold')
        
        # Set viewing angle
        ax.view_init(elev=30, azim=45)
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    @staticmethod
    def _get_grade_color(grade: str) -> str:
        """Get color for quality grade."""
        grade_colors = {
            'A': 'green',
            'B': 'yellowgreen',
            'C': 'gold',
            'D': 'orange',
            'F': 'red',
            'N/A': 'gray'
        }
        return grade_colors.get(grade, 'gray')
    
    def close_all(self):
        """Close all matplotlib figures."""
        plt.close('all')