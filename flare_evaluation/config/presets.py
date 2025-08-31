"""
Preset configurations for different evaluation scenarios.
"""

from typing import Dict, Any, List


class PresetManager:
    """Manage preset configurations for common use cases."""
    
    PRESETS = {
        'standard': {
            'name': 'Standard Evaluation',
            'description': 'Default configuration for typical sensor evaluation',
            'config': {
                'sensor': {
                    'bit_depth': 10,
                    'offset': 64,
                },
                'evaluation': {
                    'signal_threshold': 10,
                    'direct_illumination_threshold': 400,
                    'light_threshold': 600,
                },
            },
        },
        'high_sensitivity': {
            'name': 'High Sensitivity',
            'description': 'Configuration for detecting subtle flare effects',
            'config': {
                'sensor': {
                    'bit_depth': 10,
                    'offset': 64,
                },
                'evaluation': {
                    'signal_threshold': 5,
                    'direct_illumination_threshold': 150,
                    'light_threshold': 400,
                },
            },
        },
        'low_light': {
            'name': 'Low Light Conditions',
            'description': 'Optimized for low light sensor evaluation',
            'config': {
                'sensor': {
                    'bit_depth': 10,
                    'offset': 32,
                    'noise_std': 5,
                },
                'evaluation': {
                    'signal_threshold': 3,
                    'direct_illumination_threshold': 120,
                    'light_threshold': 300,
                },
            },
        },
        'high_dynamic_range': {
            'name': 'High Dynamic Range',
            'description': 'Configuration for HDR sensor evaluation',
            'config': {
                'sensor': {
                    'bit_depth': 14,
                    'max_value': 16383,
                    'offset': 256,
                },
                'evaluation': {
                    'signal_threshold': 50,
                    'direct_illumination_threshold': 2000,
                    'light_threshold': 8000,
                },
                'generation': {
                    'light_intensity': 16383,
                },
            },
        },
        'scientific': {
            'name': 'Scientific Imaging',
            'description': 'High precision configuration for scientific applications',
            'config': {
                'sensor': {
                    'bit_depth': 16,
                    'max_value': 65535,
                    'offset': 512,
                    'noise_std': 1,
                },
                'evaluation': {
                    'signal_threshold': 100,
                    'direct_illumination_threshold': 5000,
                    'light_threshold': 15000,
                    'pixel_size': 0.00345,  # mm
                },
            },
        },
        'mobile_camera': {
            'name': 'Mobile Camera Sensor',
            'description': 'Configuration for smartphone camera sensors',
            'config': {
                'sensor': {
                    'size': 1024,
                    'bit_depth': 10,
                    'offset': 64,
                    'noise_std': 3,
                },
                'evaluation': {
                    'signal_threshold': 15,
                    'direct_illumination_threshold': 180,
                    'light_threshold': 480,
                },
                'generation': {
                    'enable_cross_pattern': True,
                    'flare_intensity_range': [0.3, 0.5],
                },
            },
        },
        'automotive': {
            'name': 'Automotive Sensor',
            'description': 'Configuration for automotive imaging sensors',
            'config': {
                'sensor': {
                    'bit_depth': 12,
                    'max_value': 4095,
                    'offset': 128,
                },
                'evaluation': {
                    'signal_threshold': 20,
                    'direct_illumination_threshold': 400,
                    'light_threshold': 1200,
                },
                'generation': {
                    'enable_cross_pattern': True,
                    'enable_hot_pixels': False,  # Higher quality sensors
                },
            },
        },
        'test_minimal': {
            'name': 'Minimal Test',
            'description': 'Minimal flare for testing',
            'config': {
                'generation': {
                    'flare_intensity_range': [0.1, 0.2],
                    'flare_radius_range': [20, 30],
                    'hot_pixel_count': 5,
                },
            },
        },
        'test_severe': {
            'name': 'Severe Test',
            'description': 'Severe flare for stress testing',
            'config': {
                'generation': {
                    'flare_intensity_range': [0.5, 0.8],
                    'flare_radius_range': [60, 100],
                    'hot_pixel_count': 100,
                },
            },
        },
    }
    
    @classmethod
    def get_preset(cls, name: str) -> Dict[str, Any]:
        """
        Get a preset configuration.
        
        Args:
            name: Preset name
            
        Returns:
            Preset configuration dictionary
        """
        if name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {name}")
        
        return cls.PRESETS[name]['config'].copy()
    
    @classmethod
    def list_presets(cls) -> List[Dict[str, str]]:
        """
        List available presets.
        
        Returns:
            List of preset information dictionaries
        """
        return [
            {
                'name': key,
                'display_name': value['name'],
                'description': value['description'],
            }
            for key, value in cls.PRESETS.items()
        ]
    
    @classmethod
    def get_preset_info(cls, name: str) -> Dict[str, str]:
        """
        Get information about a preset.
        
        Args:
            name: Preset name
            
        Returns:
            Preset information dictionary
        """
        if name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {name}")
        
        preset = cls.PRESETS[name]
        return {
            'name': name,
            'display_name': preset['name'],
            'description': preset['description'],
        }
    
    @classmethod
    def apply_preset(cls, config_manager, preset_name: str):
        """
        Apply a preset to a configuration manager.
        
        Args:
            config_manager: ConfigManager instance
            preset_name: Name of preset to apply
        """
        preset_config = cls.get_preset(preset_name)
        config_manager.update(preset_config)