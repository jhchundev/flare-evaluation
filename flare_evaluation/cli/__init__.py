"""Command-line interfaces for flare evaluation."""

from .evaluate import main as evaluate_main
from .generate import main as generate_main

__all__ = ["evaluate_main", "generate_main"]