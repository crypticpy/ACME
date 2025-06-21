#!/usr/bin/env python
"""Quick run script for the analysis pipeline."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline.runner import app

if __name__ == "__main__":
    app()