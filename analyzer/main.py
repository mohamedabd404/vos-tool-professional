"""
DEPRECATED: This module has been replaced by core.audio_processor
Use analyzer.simple_main for all batch processing operations.

This file is kept for backward compatibility but will be removed in future versions.
All functionality has been moved to the unified core architecture.
"""

import warnings
warnings.warn(
    "analyzer.main is deprecated. Use analyzer.simple_main instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new unified module for backward compatibility
from analyzer.simple_main import batch_analyze_folder, batch_analyze_folder_fast
import csv
from pathlib import Path

# Backward compatibility - all functions now delegate to unified core

# Legacy CSV columns for backward compatibility
CSV_COLUMNS = [
    "Agent Name",
    "Phone Number",
    "Releasing Detection - Agent never speaks?",
    "Late Hello Detection - Agent speaks after X seconds?"
]

# All other functions have been moved to core.audio_processor
# Use analyzer.simple_main for new implementations 
 
 
 