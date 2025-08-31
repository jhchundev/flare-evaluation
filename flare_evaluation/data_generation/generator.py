"""
Advanced flare data generation with configurable patterns and noise models.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from .patterns import FlarePatternGenerator
from ..utils.io import DataWriter


class FlareDataGenerator:
    """
    Sophisticated data generator for creating synthetic sensor data with flare patterns.
    
    Supports multiple sensor configurations, noise models, and flare patterns
    for comprehensive testing and evaluation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data generator.
        
        Args:
            config: Configuration dictionary for generation parameters
        """
        self.config = config or self._default_config()
        self.pattern_generator = FlarePatternGenerator()
        self.data_writer = DataWriter()
        
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Return default generation configuration."""
        return {
            'sensor_size': 512,
            'bit_depth': 10,
            'max_value': 1023,
            'offset': 64,
            'noise_std': 2,
            'light_intensity': 1023,
            'flare_intensity_range': (0.2, 0.4),
            'flare_radius_range': (30, 50),
            'enable_cross_pattern': True,
            'enable_hot_pixels': True,
            'hot_pixel_count': 20,
        }
    
    def generate(self, 
                 light_positions: Optional[List[Tuple[int, int]]] = None,
                 preset: Optional[str] = None) -> np.ndarray:
        """
        Generate synthetic sensor data with flare patterns.
        
        Args:
            light_positions: List of (x, y) coordinates for light sources
            preset: Preset configuration name ('standard', 'severe', 'minimal')
            
        Returns:
            2D numpy array of sensor data
        """
        if preset:
            self._apply_preset(preset)
        
        size = self.config['sensor_size']
        offset = self.config['offset']
        noise_std = self.config['noise_std']
        
        # Initialize base sensor data with noise
        data = self._generate_base_noise(size, offset, noise_std)
        
        # Use default positions if none provided
        if light_positions is None:
            light_positions = self._get_default_light_positions(size)
        
        # Add light sources and flare patterns
        for x, y in light_positions:
            self._add_light_source(data, x, y)
        
        # Add additional effects
        if self.config['enable_hot_pixels']:
            self._add_hot_pixels(data)
        
        # Ensure data is within valid range
        data = np.clip(data, 0, self.config['max_value'])
        
        return data
    
    def generate_sequence(self, 
                         num_frames: int,
                         motion: bool = False) -> List[np.ndarray]:
        """
        Generate a sequence of frames with optional motion.
        
        Args:
            num_frames: Number of frames to generate
            motion: Whether to simulate light source motion
            
        Returns:
            List of 2D numpy arrays
        """
        frames = []
        size = self.config['sensor_size']
        
        # Initial light positions
        base_positions = self._get_default_light_positions(size)
        
        for i in range(num_frames):
            if motion:
                # Add motion to light positions
                positions = [
                    (x + int(10 * np.sin(i * 0.1)), 
                     y + int(10 * np.cos(i * 0.1)))
                    for x, y in base_positions
                ]
            else:
                positions = base_positions
            
            frame = self.generate(positions)
            frames.append(frame)
        
        return frames
    
    def _generate_base_noise(self, size: int, offset: float, noise_std: float) -> np.ndarray:
        """Generate base sensor noise pattern."""
        # Create correlated noise for more realistic sensor behavior
        base_noise = np.random.normal(offset, noise_std, (size, size))
        
        # Add slight spatial correlation
        from scipy.ndimage import gaussian_filter
        try:
            base_noise = gaussian_filter(base_noise, sigma=0.5)
        except:
            pass  # Fall back to uncorrelated noise if scipy not available
        
        return base_noise
    
    def _add_light_source(self, data: np.ndarray, x: int, y: int):
        """Add a light source with flare pattern at given position."""
        # Random variations for natural appearance
        flare_intensity = np.random.uniform(*self.config['flare_intensity_range'])
        flare_radius = np.random.randint(*self.config['flare_radius_range'])
        
        # Generate light source and flare
        self.pattern_generator.add_light_source(
            data, x, y,
            light_radius=3,
            light_intensity=self.config['light_intensity']
        )
        
        self.pattern_generator.add_radial_flare(
            data, x, y,
            radius=flare_radius,
            intensity=flare_intensity
        )
        
        if self.config['enable_cross_pattern']:
            self.pattern_generator.add_cross_pattern(
                data, x, y,
                length=flare_radius * 2,
                intensity=flare_intensity * 0.5
            )
    
    def _add_hot_pixels(self, data: np.ndarray):
        """Add random hot pixels to simulate sensor defects."""
        size = data.shape[0]
        count = self.config['hot_pixel_count']
        
        for _ in range(count):
            x = np.random.randint(0, size)
            y = np.random.randint(0, size)
            if data[y, x] < 900:  # Don't overwrite light sources
                data[y, x] = np.random.uniform(200, 400)
    
    def _get_default_light_positions(self, size: int) -> List[Tuple[int, int]]:
        """Get default light source positions for given sensor size."""
        # Strategic placement for comprehensive flare testing
        positions = []
        
        # Corner positions
        margin = size // 8
        positions.extend([
            (margin, margin),              # Top-left
            (size - margin, margin),        # Top-right
            (margin, size - margin),        # Bottom-left
            (size - margin, size - margin), # Bottom-right
        ])
        
        # Center and off-center positions
        center = size // 2
        positions.extend([
            (center, center),               # Center
            (center - margin, center),      # Left of center
            (center + margin, center),      # Right of center
        ])
        
        return positions
    
    def _apply_preset(self, preset: str):
        """Apply a preset configuration."""
        presets = {
            'standard': {
                'flare_intensity_range': (0.2, 0.4),
                'flare_radius_range': (30, 50),
            },
            'severe': {
                'flare_intensity_range': (0.4, 0.7),
                'flare_radius_range': (50, 80),
                'hot_pixel_count': 50,
            },
            'minimal': {
                'flare_intensity_range': (0.1, 0.2),
                'flare_radius_range': (20, 30),
                'hot_pixel_count': 5,
            },
        }
        
        if preset in presets:
            self.config.update(presets[preset])
    
    def save(self, data: np.ndarray, filepath: str):
        """
        Save generated data to file.
        
        Args:
            data: Generated sensor data
            filepath: Output file path
        """
        self.data_writer.save_csv(data, filepath)