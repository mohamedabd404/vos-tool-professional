"""
DEPRECATED: This module has been replaced by core.audio_processor
Use analyzer.simple_main for all batch processing operations.

This file is kept for backward compatibility but will be removed in future versions.
All functionality has been moved to the unified core architecture.
"""

import warnings
warnings.warn(
    "utils.fast_processor is deprecated. Use analyzer.simple_main instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new unified module for backward compatibility
from analyzer.simple_main import _batch_processor


def process_folder_fast(folder_path: str, progress_callback=None):
    """
    DEPRECATED: Use analyzer.simple_main.batch_analyze_folder_fast instead.
    Maintained for backward compatibility only.
    """
    warnings.warn(
        "process_folder_fast is deprecated. Use analyzer.simple_main functions instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Delegate to new unified implementation
    results = _batch_processor.process_folder_parallel(folder_path, progress_callback)
    return results