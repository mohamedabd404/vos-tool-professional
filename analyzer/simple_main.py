"""
Unified analyzer module using optimized core components.
Provides clean interface for batch processing with proper channel separation.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from core.audio_processor import AudioProcessor, convert_to_dataframe_format


class BatchProcessor:
    """
    Optimized batch processor using unified audio processing logic.
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        self.audio_processor = AudioProcessor()
        self.max_workers = max_workers or min(os.cpu_count() * 2, 16)  # Reasonable limit
    
    def find_audio_files(self, folder_path: str) -> List[Path]:
        """
        Find all audio files in folder and subdirectories.
        
        Args:
            folder_path: Path to search
            
        Returns:
            List of audio file paths
        """
        folder = Path(folder_path)
        if not folder.exists():
            return []
        
        # Search for supported audio formats
        audio_files = []
        for pattern in ['*.mp3', '*.wav', '*.m4a', '*.mp4']:
            audio_files.extend(folder.rglob(pattern))
        
        return audio_files
    
    def process_folder_parallel(self, folder_path: str, progress_callback: Optional[Callable] = None) -> List[dict]:
        """
        Process all audio files in folder using parallel processing.
        
        Args:
            folder_path: Path to folder containing audio files
            progress_callback: Optional progress callback (done, total)
            
        Returns:
            List of processing results
        """
        audio_files = self.find_audio_files(folder_path)
        
        if not audio_files:
            return []
        
        results = []
        total_files = len(audio_files)
        
        # Process files in parallel batches
        batch_size = 20  # Process 20 files at a time
        
        for i in range(0, total_files, batch_size):
            batch_files = audio_files[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit batch for processing
                futures = [
                    executor.submit(self.audio_processor.process_single_file, file_path)
                    for file_path in batch_files
                ]
                
                # Collect results as they complete
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        # Handle individual file processing errors
                        results.append({
                            'agent_name': 'Unknown',
                            'phone_number': '',
                            'file_path': 'Unknown',
                            'error': f"Processing error: {str(e)}",
                            'classification_success': False
                        })
            
            # Update progress
            if progress_callback:
                done = min(i + batch_size, total_files)
                progress_callback(done, total_files)
        
        return results


# Global batch processor instance
_batch_processor = BatchProcessor()


def batch_analyze_folder(folder_path: str) -> pd.DataFrame:
    """
    Analyze all audio files in a folder and return results as pandas DataFrame.
    Uses optimized core audio processing with proper channel separation.
    
    Args:
        folder_path: Path to folder containing audio files
        
    Returns:
        pandas DataFrame with analysis results for flagged calls only
    """
    results = _batch_processor.process_folder_parallel(folder_path)
    flagged_calls = convert_to_dataframe_format(results)
    return pd.DataFrame(flagged_calls)


def batch_analyze_folder_fast(folder_path: str, progress_callback: Optional[Callable] = None) -> pd.DataFrame:
    """
    Fast batch analysis with progress tracking and proper channel separation.
    
    Args:
        folder_path: Path to folder containing audio files
        progress_callback: Optional callback function for progress updates (done, total)
        
    Returns:
        pandas DataFrame with analysis results for flagged calls only
    """
    results = _batch_processor.process_folder_parallel(folder_path, progress_callback)
    flagged_calls = convert_to_dataframe_format(results)
    return pd.DataFrame(flagged_calls)
