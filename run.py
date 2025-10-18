#!/usr/bin/env python
"""
Main Runner Script - Farm Stock Prediction System

This is the entry point for running the complete pipeline.
All scripts are organized in the scripts/ folder.
"""

import subprocess
import sys
import os

# Change to project root if needed
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("🚀 FARM STOCK PREDICTION SYSTEM")
print("="*80)
print("\nRunning complete pipeline from scripts/ folder...\n")

# Run the complete pipeline script
result = subprocess.run(
    [sys.executable, 'scripts/run_complete_pipeline.py'],
    cwd=os.getcwd()
)

sys.exit(result.returncode)
