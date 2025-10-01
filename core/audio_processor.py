"""
Core Audio Processing Module
Unified, optimized audio processing with proper channel separation and detection logic.
Eliminates duplication and ensures consistent behavior across all modules.
"""

import time
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from pydub import AudioSegment
from analyzer.intro_detection import releasing_detection, late_hello_detection, debug_audio_analysis


def format_agent_name_with_spaces(agent_name: str) -> str:
    """
    Convert agent names from formats like 'AbdelrahmanAhmedIbrahimHassan' 
    to 'Abdelrahman Ahmed Ibrahim Hassan' by adding spaces before capital letters.
    
    This handles names that were stored without spaces in filenames.
    
    Args:
        agent_name: Agent name without spaces (e.g., 'JohnSmith' or 'AbdelrahmanAhmed')
        
    Returns:
        Agent name with spaces (e.g., 'John Smith' or 'Abdelrahman Ahmed')
    """
    # If name already has spaces, return as-is
    if ' ' in agent_name:
        return agent_name
    
    # Add space before each capital letter (except the first one)
    # This handles camelCase like 'JohnSmith' -> 'John Smith'
    spaced_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', agent_name)
    
    return spaced_name


class AudioProcessor:
    """
    Unified audio processor for VOS Tool.
    Handles file loading, channel separation, and call classification.
    """
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.mp4']
        
    def is_valid_audio_file(self, file_path: Path) -> bool:
        """
        Validate audio file before processing.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if file is valid for processing
        """
        try:
            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return False
            
            # Check file size (should be > 1KB for valid audio)
            file_size = file_path.stat().st_size
            if file_size < 1024:
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.supported_formats:
                return False
            
            return True
            
        except Exception:
            return False
    
    def load_audio_file(self, file_path: Path) -> Optional[AudioSegment]:
        """
        Load audio file with format fallback support.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioSegment or None if loading fails
        """
        try:
            # Try loading as MP3 first (most common)
            return AudioSegment.from_mp3(file_path)
            
        except Exception:
            # Fallback: try different formats
            for format_name in ['wav', 'mp4', 'm4a']:
                try:
                    return AudioSegment.from_file(str(file_path), format=format_name)
                except:
                    continue
            
            return None
    
    def extract_agent_audio(self, audio: AudioSegment) -> AudioSegment:
        """
        Extract agent audio channel from recording.
        
        Specification:
        - Stereo: Left channel = Agent, Right channel = Customer
        - Mono: Entire audio = Agent
        
        Args:
            audio: Full audio segment
            
        Returns:
            Agent audio channel only
        """
        if audio.channels == 2:
            # Split stereo and return left channel (agent)
            return audio.split_to_mono()[0]
        else:
            # Mono audio - assume it's agent channel
            return audio
    
    def classify_call(self, agent_audio: AudioSegment, file_name: str = "Unknown") -> Dict:
        """
        Classify call using deterministic rules.
        
        Args:
            agent_audio: Agent audio channel only
            file_name: File name for debugging
            
        Returns:
            Classification results with standardized keys
        """
        try:
            # Apply detection functions
            releasing_result = releasing_detection(agent_audio)
            late_hello_result = late_hello_detection(agent_audio)
            
            return {
                "releasing_detection": releasing_result,
                "late_hello_detection": late_hello_result,
                "classification_success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "releasing_detection": "Error",
                "late_hello_detection": "Error", 
                "classification_success": False,
                "error": str(e)
            }
    
    def process_single_file(self, file_path: Path, include_debug: bool = False) -> Dict:
        """
        Process a single audio file end-to-end.
        
        Args:
            file_path: Path to audio file
            include_debug: Whether to include detailed debug information
            
        Returns:
            Complete processing results
        """
        start_time = time.time()
        
        # Extract metadata from filename
        stem = file_path.stem
        if "_" in stem:
            parts = stem.split("_", 1)
            if len(parts) == 2:
                agent_name_raw, phone_number = parts
            else:
                agent_name_raw, phone_number = stem, ""
        else:
            agent_name_raw, phone_number = stem, ""
        
        # Clean up agent name - remove special characters but keep the structure
        agent_name_raw = agent_name_raw.replace("-", "").replace(".", "")
        
        # Format agent name with proper spacing (converts 'JohnSmith' to 'John Smith')
        agent_name = format_agent_name_with_spaces(agent_name_raw)
        
        # Validate file
        if not self.is_valid_audio_file(file_path):
            return {
                'agent_name': agent_name,
                'phone_number': phone_number,
                'file_path': str(file_path),
                'error': f"Invalid audio file: {file_path}",
                'processing_time': time.time() - start_time,
                'classification_success': False
            }
        
        # Load audio
        audio = self.load_audio_file(file_path)
        if audio is None:
            return {
                'agent_name': agent_name,
                'phone_number': phone_number,
                'file_path': str(file_path),
                'error': f"Failed to load audio: {file_path}",
                'processing_time': time.time() - start_time,
                'classification_success': False
            }
        
        # Extract agent channel
        agent_audio = self.extract_agent_audio(audio)
        
        # Validate audio length
        if len(agent_audio) < 1000:  # Less than 1 second
            return {
                'agent_name': agent_name,
                'phone_number': phone_number,
                'file_path': str(file_path),
                'error': f"Audio too short: {len(agent_audio)}ms",
                'processing_time': time.time() - start_time,
                'classification_success': False
            }
        
        # Classify call
        classification = self.classify_call(agent_audio, file_name=file_path.name)
        
        # Build result
        result = {
            'agent_name': agent_name,
            'phone_number': phone_number,
            'file_path': str(file_path),
            'processing_time': time.time() - start_time,
            'classification_success': classification['classification_success'],
            'releasing_detection': classification['releasing_detection'],
            'late_hello_detection': classification['late_hello_detection']
        }
        
        if classification['error']:
            result['error'] = classification['error']
        
        # Add debug information if requested
        if include_debug:
            try:
                debug_info = debug_audio_analysis(agent_audio, file_path.name)
                result['debug_info'] = debug_info
            except Exception as e:
                result['debug_error'] = str(e)
        
        return result
    
    def process_batch(self, file_paths: List[Path], include_debug: bool = False) -> List[Dict]:
        """
        Process multiple audio files.
        
        Args:
            file_paths: List of audio file paths
            include_debug: Whether to include debug information
            
        Returns:
            List of processing results
        """
        results = []
        for file_path in file_paths:
            result = self.process_single_file(file_path, include_debug)
            results.append(result)
        
        return results


# Standardized result keys for consistency across modules
RESULT_KEYS = {
    "AGENT_NAME": "Agent Name",
    "PHONE_NUMBER": "Phone Number", 
    "RELEASING": "Releasing Detection - Agent never speaks?",
    "LATE_HELLO": "Late Hello Detection - Agent speaks after X seconds?"
}


def convert_to_dataframe_format(results: List[Dict]) -> List[Dict]:
    """
    Convert processing results to standardized DataFrame format.
    Only includes flagged calls (with detected issues).
    
    Args:
        results: List of processing results
        
    Returns:
        List of dictionaries ready for DataFrame conversion
    """
    flagged_calls = []
    
    for result in results:
        # Skip files with errors
        if not result.get('classification_success', False):
            continue
        
        # Check if any detection is flagged
        releasing_flagged = result.get('releasing_detection') == "Yes"
        late_hello_flagged = result.get('late_hello_detection') == "Yes"
        
        # Only include flagged calls
        if releasing_flagged or late_hello_flagged:
            flagged_calls.append({
                RESULT_KEYS["AGENT_NAME"]: result.get('agent_name', ''),
                RESULT_KEYS["PHONE_NUMBER"]: result.get('phone_number', ''),
                RESULT_KEYS["RELEASING"]: result.get('releasing_detection', 'No'),
                RESULT_KEYS["LATE_HELLO"]: result.get('late_hello_detection', 'No')
            })
    
    return flagged_calls
