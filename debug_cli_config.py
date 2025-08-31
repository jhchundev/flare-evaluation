#!/usr/bin/env python3
"""
Debug what configuration the CLI is actually using.
"""

from flare_evaluation.config import ConfigManager
from flare_evaluation import FlareEvaluator

# Test what the config manager returns
config_manager = ConfigManager()
print("=== CONFIG MANAGER TEST ===")
print("Default config loaded:", config_manager.config)

evaluation_config = config_manager.export_section('evaluation')
print("Evaluation section:", evaluation_config)

# Create evaluator with CLI config
print("\n=== EVALUATOR WITH CLI CONFIG ===")
evaluator_cli = FlareEvaluator(evaluation_config)
print("CLI evaluator config:", evaluator_cli.config)

# Create evaluator with default config
print("\n=== EVALUATOR WITH DEFAULT CONFIG ===")
evaluator_default = FlareEvaluator()
print("Default evaluator config:", evaluator_default.config)

# Check which presets are available
from flare_evaluation.config import PresetManager
preset_manager = PresetManager()
print("\n=== AVAILABLE PRESETS ===")
for preset_name in preset_manager.get_available_presets():
    preset = preset_manager.get_preset(preset_name)
    eval_config = preset['config'].get('evaluation', {})
    print(f"{preset_name}: light_threshold={eval_config.get('light_threshold', 'N/A')}, direct_illumination_threshold={eval_config.get('direct_illumination_threshold', 'N/A')}")

# Test actual evaluation with both configs
import numpy as np
data = np.loadtxt('data/gemini_flare_10bit.csv', delimiter=',')

print(f"\n=== EVALUATION COMPARISON ===")
results_cli = evaluator_cli.evaluate(data)
results_default = evaluator_default.evaluate(data)

print(f"CLI config results:")
print(f"  Direct illumination pixels: {results_cli.get('direct_illumination_pixel_count', 'MISSING')}")
print(f"  Light source pixels: {results_cli['light_pixel_count']}")

print(f"Default config results:")  
print(f"  Direct illumination pixels: {results_default.get('direct_illumination_pixel_count', 'MISSING')}")
print(f"  Light source pixels: {results_default['light_pixel_count']}")
