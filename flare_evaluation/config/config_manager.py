"""
Configuration management system for flare evaluation.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Centralized configuration management for the flare evaluation system.
    
    Handles loading, saving, and validation of configuration parameters
    across all modules.
    """
    
    DEFAULT_CONFIG = {
        'sensor': {
            'size': 512,
            'bit_depth': 10,
            'max_value': 1023,
            'offset': 64,
            'noise_std': 2,
        },
        'evaluation': {
            'signal_threshold': 10,
            'direct_illumination_threshold': 400,
            'light_threshold': 600,
            'pixel_size': 1.0,
            'light_amount': 1.0,
        },
        'generation': {
            'light_intensity': 1023,
            'flare_intensity_range': [0.2, 0.4],
            'flare_radius_range': [30, 50],
            'enable_cross_pattern': True,
            'enable_hot_pixels': True,
            'hot_pixel_count': 20,
        },
        'visualization': {
            'output_format': 'pgm',
            'colormap': 'viridis',
            'dpi': 100,
        },
        'processing': {
            'batch_size': 10,
            'parallel': False,
            'cache_results': True,
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load(config_path)
    
    def load(self, filepath: str):
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to configuration file
        """
        with open(filepath, 'r') as f:
            loaded_config = json.load(f)
        
        # Merge with defaults
        self.config = self._deep_merge(self.DEFAULT_CONFIG, loaded_config)
        self.config_path = filepath
    
    def save(self, filepath: Optional[str] = None):
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save configuration (uses loaded path if not specified)
        """
        save_path = filepath or self.config_path
        if not save_path:
            raise ValueError("No save path specified")
        
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'sensor.bit_depth')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'sensor.bit_depth')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of updates
        """
        self.config = self._deep_merge(self.config, updates)
    
    def reset(self, section: Optional[str] = None):
        """
        Reset configuration to defaults.
        
        Args:
            section: Specific section to reset (e.g., 'sensor')
        """
        if section:
            if section in self.DEFAULT_CONFIG:
                self.config[section] = self.DEFAULT_CONFIG[section].copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate current configuration.
        
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
        }
        
        # Sensor validation
        sensor = self.config.get('sensor', {})
        if sensor.get('bit_depth', 10) > 16:
            results['warnings'].append("Bit depth > 16 may cause memory issues")
        
        if sensor.get('size', 512) > 2048:
            results['warnings'].append("Large sensor size may impact performance")
        
        # Evaluation validation
        eval_config = self.config.get('evaluation', {})
        if eval_config.get('signal_threshold', 0) >= eval_config.get('light_threshold', 255):
            results['errors'].append("Signal threshold must be less than light threshold")
            results['valid'] = False
        
        # Generation validation
        gen_config = self.config.get('generation', {})
        flare_range = gen_config.get('flare_intensity_range', [0, 1])
        if flare_range[0] > flare_range[1]:
            results['errors'].append("Invalid flare intensity range")
            results['valid'] = False
        
        return results
    
    def export_section(self, section: str) -> Dict[str, Any]:
        """
        Export a specific configuration section.
        
        Args:
            section: Section name to export
            
        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {}).copy()
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            updates: Updates to apply
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.copy()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ConfigManager(sections={list(self.config.keys())})"