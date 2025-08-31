#!/usr/bin/env python3
"""
Main entry point for running the flare evaluator.
Wrapper script for the new modular CLI interface.
"""

import sys
from flare_evaluation.cli.evaluate import main

if __name__ == '__main__':
    sys.exit(main())