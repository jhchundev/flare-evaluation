"""
Flare pattern generation algorithms for realistic optical effects.
"""

import numpy as np
import math
from typing import Optional


class FlarePatternGenerator:
    """Generate various flare patterns for optical simulation."""
    
    def add_light_source(self, 
                        grid: np.ndarray,
                        center_x: int, 
                        center_y: int,
                        light_radius: int = 3,
                        light_intensity: float = 1023):
        """
        Add a bright light source to the grid.
        
        Args:
            grid: 2D array to modify
            center_x, center_y: Center coordinates
            light_radius: Radius of light source
            light_intensity: Intensity value for light pixels
        """
        height, width = grid.shape
        
        for dy in range(-light_radius, light_radius + 1):
            for dx in range(-light_radius, light_radius + 1):
                y, x = center_y + dy, center_x + dx
                if 0 <= y < height and 0 <= x < width:
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist <= light_radius:
                        # Gaussian falloff at edges
                        intensity = light_intensity
                        if dist > light_radius * 0.7:
                            falloff = math.exp(-((dist - light_radius * 0.7) ** 2) / 2)
                            intensity = light_intensity * falloff
                        grid[y, x] = max(grid[y, x], intensity)
    
    def add_radial_flare(self,
                        grid: np.ndarray,
                        center_x: int,
                        center_y: int,
                        radius: int = 50,
                        intensity: float = 0.3,
                        decay_rate: float = 15):
        """
        Add radial flare pattern with exponential decay.
        
        Args:
            grid: 2D array to modify
            center_x, center_y: Center coordinates
            radius: Maximum flare radius
            intensity: Base flare intensity
            decay_rate: Exponential decay rate
        """
        height, width = grid.shape
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                y, x = center_y + dy, center_x + dx
                if 0 <= y < height and 0 <= x < width:
                    dist = math.sqrt(dx**2 + dy**2)
                    if 3 < dist <= radius:  # Skip light source area
                        # Exponential decay with distance
                        decay = math.exp(-dist / decay_rate)
                        flare_value = intensity * decay * 200
                        
                        # Add angular variation for realism
                        angle = math.atan2(dy, dx)
                        angular_mod = 1 + 0.2 * math.sin(angle * 6)
                        flare_value *= angular_mod
                        
                        if flare_value > 10 and grid[y, x] < 900:
                            grid[y, x] = min(250, grid[y, x] + flare_value)
    
    def add_cross_pattern(self,
                         grid: np.ndarray,
                         center_x: int,
                         center_y: int,
                         length: int = 100,
                         intensity: float = 0.2,
                         angle: float = 0):
        """
        Add cross-shaped flare pattern (diffraction spikes).
        
        Args:
            grid: 2D array to modify
            center_x, center_y: Center coordinates
            length: Length of cross arms
            intensity: Cross pattern intensity
            angle: Rotation angle in radians
        """
        height, width = grid.shape
        
        # Create four spikes
        spike_angles = [angle + i * math.pi/2 for i in range(4)]
        
        for spike_angle in spike_angles:
            for dist in range(4, length):  # Start from outside light source
                # Calculate position along spike
                x = center_x + int(dist * math.cos(spike_angle))
                y = center_y + int(dist * math.sin(spike_angle))
                
                if 0 <= y < height and 0 <= x < width:
                    # Exponential decay along spike
                    decay = math.exp(-dist / 25)
                    
                    # Add slight width to spike
                    for width_offset in range(-1, 2):
                        x_w = x + int(width_offset * math.sin(spike_angle))
                        y_w = y - int(width_offset * math.cos(spike_angle))
                        
                        if 0 <= y_w < height and 0 <= x_w < width:
                            width_factor = 1.0 if width_offset == 0 else 0.3
                            flare_value = intensity * decay * 150 * width_factor
                            
                            if flare_value > 10 and grid[y_w, x_w] < 900:
                                grid[y_w, x_w] = min(250, grid[y_w, x_w] + flare_value)
    
    def add_ghosting(self,
                    grid: np.ndarray,
                    center_x: int,
                    center_y: int,
                    offset_x: int,
                    offset_y: int,
                    intensity: float = 0.1):
        """
        Add lens ghosting effect (secondary reflection).
        
        Args:
            grid: 2D array to modify
            center_x, center_y: Original light source position
            offset_x, offset_y: Ghost offset from center
            intensity: Ghost intensity relative to source
        """
        height, width = grid.shape
        
        # Ghost position (typically opposite side of center)
        ghost_x = center_x + offset_x
        ghost_y = center_y + offset_y
        
        if 0 <= ghost_y < height and 0 <= ghost_x < width:
            # Add dimmer version of light source
            self.add_light_source(grid, ghost_x, ghost_y, 
                                light_radius=2, 
                                light_intensity=intensity * 500)
            
            # Add subtle flare around ghost
            self.add_radial_flare(grid, ghost_x, ghost_y,
                                radius=20,
                                intensity=intensity * 0.5)
    
    def add_chromatic_aberration(self,
                                grid_r: np.ndarray,
                                grid_g: np.ndarray, 
                                grid_b: np.ndarray,
                                center_x: int,
                                center_y: int):
        """
        Simulate chromatic aberration for RGB channels.
        
        Args:
            grid_r, grid_g, grid_b: RGB channel arrays
            center_x, center_y: Light source position
        """
        # Different wavelengths focus at slightly different positions
        self.add_radial_flare(grid_r, center_x - 1, center_y, radius=52)
        self.add_radial_flare(grid_g, center_x, center_y, radius=50)
        self.add_radial_flare(grid_b, center_x + 1, center_y, radius=48)
    
    def add_bloom(self,
                 grid: np.ndarray,
                 threshold: float = 200,
                 intensity: float = 0.3):
        """
        Add bloom effect to bright areas.
        
        Args:
            grid: 2D array to modify
            threshold: Brightness threshold for bloom
            intensity: Bloom intensity
        """
        try:
            from scipy.ndimage import gaussian_filter
            
            # Extract bright regions
            bright_mask = grid > threshold
            bloom_source = np.where(bright_mask, grid - threshold, 0)
            
            # Apply gaussian blur for bloom
            bloom = gaussian_filter(bloom_source, sigma=5) * intensity
            
            # Add bloom back to image
            grid += bloom
            np.clip(grid, 0, 1023, out=grid)
        except ImportError:
            pass  # Skip if scipy not available