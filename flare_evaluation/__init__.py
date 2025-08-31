"""
Flare Evaluation Package
A comprehensive toolkit for optical flare analysis in sensor data.
"""

__version__ = "1.0.0"
__author__ = "Flare Evaluation Team"

from .core.evaluator import FlareEvaluator
from .data_generation.generator import FlareDataGenerator
from .visualization.visualizer import FlareVisualizer

__all__ = [
    "FlareEvaluator",
    "FlareDataGenerator", 
    "FlareVisualizer",
]