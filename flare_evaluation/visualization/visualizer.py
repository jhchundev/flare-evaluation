"""
Advanced visualization for flare analysis results.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from ..utils.io import ImageWriter


class FlareVisualizer:
    """
    Comprehensive visualization system for flare evaluation results.
    
    Generates various visual representations including masks, heatmaps,
    and analytical plots for flare analysis.
    """
    
    def __init__(self):
        """Initialize the visualizer."""
        self.image_writer = ImageWriter()
        
    def create_flare_mask(self, 
                         data: np.ndarray,
                         config: Dict[str, Any]) -> np.ndarray:
        """
        Create a binary mask highlighting flare regions.
        
        Args:
            data: Sensor data array
            config: Evaluation configuration
            
        Returns:
            Binary mask (0 or 255)
        """
        offset = config['offset']
        signal_threshold = config['signal_threshold']
        light_threshold = config['light_threshold']
        
        # Identify flare regions
        flare_condition = (
            (data > offset + signal_threshold) & 
            (data < light_threshold)
        )
        
        # Create binary mask
        mask = np.where(flare_condition, 255, 0).astype(np.uint8)
        
        return mask
    
    def create_composite_visualization(self,
                                     data: np.ndarray,
                                     evaluation_result: Dict[str, Any]) -> np.ndarray:
        """
        Create a composite visualization with multiple overlays.
        
        Args:
            data: Original sensor data
            evaluation_result: Results from flare evaluation
            
        Returns:
            Composite visualization array
        """
        # Normalize data to 0-255 range
        normalized = self._normalize_to_uint8(data)
        
        # Create RGB composite
        composite = np.stack([normalized, normalized, normalized], axis=-1)
        
        # Overlay flare regions in yellow
        flare_mask = evaluation_result.get('flare_mask', np.zeros_like(data))
        composite[flare_mask > 0] = [255, 255, 0]  # Yellow for flare
        
        # Overlay direct illumination regions in orange
        direct_illumination_mask = evaluation_result.get('direct_illumination_mask', np.zeros_like(data))
        composite[direct_illumination_mask > 0] = [255, 165, 0]  # Orange for direct illumination
        
        # Overlay light source cores in red
        light_mask = evaluation_result.get('light_mask', np.zeros_like(data))
        composite[light_mask > 0] = [255, 0, 0]  # Red for light source cores
        
        return composite
    
    def create_intensity_heatmap(self, 
                                data: np.ndarray,
                                colormap: str = 'viridis') -> np.ndarray:
        """
        Create an intensity heatmap of the sensor data.
        
        Args:
            data: Sensor data array
            colormap: Color mapping scheme
            
        Returns:
            Colored heatmap array
        """
        normalized = self._normalize_to_uint8(data)
        
        # Apply colormap
        if colormap == 'viridis':
            heatmap = self._apply_viridis(normalized)
        elif colormap == 'plasma':
            heatmap = self._apply_plasma(normalized)
        elif colormap == 'inferno':
            heatmap = self._apply_inferno(normalized)
        else:
            # Default grayscale
            heatmap = np.stack([normalized, normalized, normalized], axis=-1)
        
        return heatmap
    
    def create_contour_map(self,
                          data: np.ndarray,
                          levels: int = 10) -> np.ndarray:
        """
        Create a contour map showing intensity levels.
        
        Args:
            data: Sensor data array
            levels: Number of contour levels
            
        Returns:
            Contour visualization array
        """
        # Create contour levels
        min_val, max_val = data.min(), data.max()
        level_values = np.linspace(min_val, max_val, levels)
        
        # Create contour visualization
        contour = np.zeros_like(data, dtype=np.uint8)
        
        for i, level in enumerate(level_values[:-1]):
            mask = (data >= level) & (data < level_values[i + 1])
            contour[mask] = int(255 * (i + 1) / levels)
        
        return contour
    
    def create_3d_surface_data(self, 
                              data: np.ndarray,
                              downsample: int = 4) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for 3D surface plotting.
        
        Args:
            data: Sensor data array
            downsample: Downsampling factor for performance
            
        Returns:
            Tuple of (X, Y, Z) arrays for 3D plotting
        """
        # Downsample for performance
        if downsample > 1:
            data = data[::downsample, ::downsample]
        
        height, width = data.shape
        x = np.arange(0, width)
        y = np.arange(0, height)
        X, Y = np.meshgrid(x, y)
        
        return X, Y, data
    
    def save_visualization(self, 
                         visualization: np.ndarray,
                         filepath: str,
                         format: str = 'pgm',
                         **kwargs):
        """
        Save visualization to file with format-specific options.
        
        Args:
            visualization: Visualization array
            filepath: Output file path
            format: Output format ('pgm', 'png', 'jpg', 'tiff')
            **kwargs: Format-specific options:
                - For PNG: compress_level (0-9), optimize (bool), dpi (int)
                - For JPG: quality (0-100), optimize (bool), dpi (int)
                - For all: colormap (str) to apply color mapping
        """
        if format == 'pgm':
            self.image_writer.save_pgm(visualization, filepath)
        elif 'colormap' in kwargs:
            # Save with colormap
            colormap = kwargs.pop('colormap')
            self.image_writer.save_with_colormap(
                visualization, filepath, colormap, format
            )
        else:
            # Save with format-specific options
            self.image_writer.save_image(visualization, filepath, format, **kwargs)
    
    def export_as_png(self,
                     data: np.ndarray,
                     evaluation_result: Dict[str, Any],
                     filepath: str,
                     mode: str = 'composite',
                     colormap: Optional[str] = None,
                     dpi: int = 100,
                     compress_level: int = 6):
        """
        Export visualization as PNG with various modes.
        
        Args:
            data: Original sensor data
            evaluation_result: Results from evaluation
            filepath: Output PNG file path
            mode: Visualization mode:
                - 'composite': Colored overlay with flare and light sources
                - 'mask': Binary flare mask
                - 'heatmap': Intensity heatmap
                - 'original': Original data with colormap
            colormap: Color mapping for visualization
            dpi: Dots per inch for the PNG
            compress_level: PNG compression level (0-9)
        """
        if mode == 'composite':
            vis = self.create_composite_visualization(data, evaluation_result)
        elif mode == 'mask':
            vis = evaluation_result.get('flare_mask', np.zeros_like(data))
        elif mode == 'heatmap':
            vis = self.create_intensity_heatmap(data, colormap or 'viridis')
        elif mode == 'original':
            vis = self._normalize_to_uint8(data)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        # Save PNG with options
        if colormap and mode != 'composite' and mode != 'heatmap':
            self.image_writer.save_with_colormap(
                vis, filepath, colormap, 'png'
            )
        else:
            self.image_writer.save_png(
                vis, filepath,
                compress_level=compress_level,
                optimize=True,
                dpi=dpi
            )
    
    def export_multi_panel(self,
                         data: np.ndarray,
                         evaluation_result: Dict[str, Any],
                         filepath: str,
                         panels: List[str] = None,
                         layout: Tuple[int, int] = (2, 2)):
        """
        Export multi-panel visualization as PNG.
        
        Args:
            data: Original sensor data
            evaluation_result: Evaluation results
            filepath: Output PNG file path
            panels: List of panel types to include
            layout: Grid layout (rows, cols)
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            if panels is None:
                panels = ['original', 'mask', 'composite', 'heatmap']
            
            # Generate individual panels
            panel_images = []
            
            for panel_type in panels:
                if panel_type == 'original':
                    panel = self._normalize_to_uint8(data)
                elif panel_type == 'mask':
                    panel = evaluation_result.get('flare_mask', np.zeros_like(data))
                elif panel_type == 'composite':
                    panel = self.create_composite_visualization(data, evaluation_result)
                elif panel_type == 'heatmap':
                    panel = self.create_intensity_heatmap(data, 'viridis')
                elif panel_type == 'contour':
                    panel = self.create_contour_map(data)
                else:
                    continue
                
                # Convert to PIL Image
                if len(panel.shape) == 2:
                    img = Image.fromarray(panel.astype(np.uint8), mode='L')
                    img = img.convert('RGB')  # Convert to RGB for consistency
                else:
                    img = Image.fromarray(panel.astype(np.uint8), mode='RGB')
                
                panel_images.append((panel_type, img))
            
            # Calculate panel size
            rows, cols = layout
            if len(panel_images) > 0:
                panel_width = panel_images[0][1].width
                panel_height = panel_images[0][1].height
            else:
                return
            
            # Create combined image
            margin = 10
            text_height = 20
            
            combined_width = cols * panel_width + (cols + 1) * margin
            combined_height = rows * (panel_height + text_height) + (rows + 1) * margin
            
            combined = Image.new('RGB', (combined_width, combined_height), 'white')
            draw = ImageDraw.Draw(combined)
            
            # Place panels
            for idx, (title, img) in enumerate(panel_images[:rows*cols]):
                row = idx // cols
                col = idx % cols
                
                x = col * panel_width + (col + 1) * margin
                y = row * (panel_height + text_height) + (row + 1) * margin + text_height
                
                # Paste image
                combined.paste(img, (x, y))
                
                # Add title
                text_x = x + panel_width // 2
                text_y = y - text_height + 5
                draw.text((text_x, text_y), title.title(), 
                         fill='black', anchor='mt')
            
            # Save combined image
            combined.save(filepath, 'PNG', optimize=True, dpi=(100, 100))
            
        except ImportError:
            print("Warning: Pillow not installed, cannot create multi-panel export")
            # Fall back to single panel
            self.export_as_png(data, evaluation_result, filepath, mode='composite')
    
    def _normalize_to_uint8(self, data: np.ndarray) -> np.ndarray:
        """Normalize data to 0-255 uint8 range."""
        min_val = data.min()
        max_val = data.max()
        
        if max_val > min_val:
            normalized = (data - min_val) / (max_val - min_val) * 255
        else:
            normalized = np.zeros_like(data)
        
        return normalized.astype(np.uint8)
    
    def _apply_viridis(self, gray: np.ndarray) -> np.ndarray:
        """Apply viridis colormap to grayscale image."""
        # Simplified viridis colormap
        r = np.clip(gray * 0.3 + 50, 0, 255)
        g = np.clip(gray * 0.8 + 20, 0, 255)
        b = np.clip(255 - gray * 0.5, 0, 255)
        
        return np.stack([r, g, b], axis=-1).astype(np.uint8)
    
    def _apply_plasma(self, gray: np.ndarray) -> np.ndarray:
        """Apply plasma colormap to grayscale image."""
        r = np.clip(gray * 1.2, 0, 255)
        g = np.clip(gray * 0.3, 0, 255)
        b = np.clip(255 - gray * 0.8, 0, 255)
        
        return np.stack([r, g, b], axis=-1).astype(np.uint8)
    
    def _apply_inferno(self, gray: np.ndarray) -> np.ndarray:
        """Apply inferno colormap to grayscale image."""
        r = np.clip(gray * 1.5, 0, 255)
        g = np.clip(gray * 0.7 - 50, 0, 255)
        b = np.clip(gray * 0.2, 0, 255)
        
        return np.stack([r, g, b], axis=-1).astype(np.uint8)