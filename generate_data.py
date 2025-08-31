#!/usr/bin/env python3
"""
Main entry point for generating flare experiment data.
Wrapper script for the new modular CLI interface.
"""

import sys
from flare_evaluation.cli.generate import main

if __name__ == "__main__":
    # If no arguments provided, generate default 10-bit data
    if len(sys.argv) == 1:
        sys.argv.extend(['data/flare_experiment_10bit.csv', '--preset', 'standard'])
    
    sys.exit(main())