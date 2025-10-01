from pydub import AudioSegment
import numpy as np
from pydub.silence import detect_silence
from config import app_settings
from scipy import signal
from scipy.fft import rfft, rfftfreq

def extract_left_channel(audio_segment):
    """
    Extract left channel (agent) from stereo audio.
    If mono, return the original segment.
    """
    if audio_segment.channels == 2:
        # Split stereo into left and right channels
        left_channel = audio_segment.split_to_mono()[0]
        return left_channel
    else:
        # Already mono, assume it's the agent channel
        return audio_segment

def estimate_noise_floor(audio_array, frame_rate, percentile=10):
    """
    Estimate adaptive noise floor from audio signal.
    Uses the lower percentile of frame energies to determine baseline noise.
    
    Args:
        audio_array: Normalized audio array
        frame_rate: Sample rate
        percentile: Percentile to use for noise floor (default 10th percentile)
    
    Returns:
        Noise floor energy level
    """
    frame_length = int(0.05 * frame_rate)  # 50ms frames
    hop_length = int(0.025 * frame_rate)   # 25ms hop
    
    frame_energies = []
    for i in range(0, len(audio_array) - frame_length, hop_length):
        frame = audio_array[i:i + frame_length]
        rms = np.sqrt(np.mean(frame**2)) * 32767
        frame_energies.append(rms)
    
    if len(frame_energies) == 0:
        return 0
    
    # Use percentile to estimate noise floor
    noise_floor = np.percentile(frame_energies, percentile)
    return noise_floor


def calculate_spectral_features(frame, frame_rate):
    """
    Calculate spectral features to distinguish speech from noise.
    
    Args:
        frame: Audio frame (numpy array)
        frame_rate: Sample rate
    
    Returns:
        dict with spectral_centroid, spectral_bandwidth, spectral_rolloff
    """
    try:
        # Compute FFT
        fft_vals = np.abs(rfft(frame))
        fft_freqs = rfftfreq(len(frame), 1.0 / frame_rate)
        
        # Avoid division by zero
        if np.sum(fft_vals) == 0:
            return {'centroid': 0, 'bandwidth': 0, 'rolloff': 0}
        
        # Spectral centroid (center of mass of spectrum)
        centroid = np.sum(fft_freqs * fft_vals) / np.sum(fft_vals)
        
        # Spectral bandwidth (spread around centroid)
        bandwidth = np.sqrt(np.sum(((fft_freqs - centroid) ** 2) * fft_vals) / np.sum(fft_vals))
        
        # Spectral rolloff (frequency below which 85% of energy is contained)
        cumsum = np.cumsum(fft_vals)
        rolloff_idx = np.where(cumsum >= 0.85 * cumsum[-1])[0]
        rolloff = fft_freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0
        
        return {
            'centroid': centroid,
            'bandwidth': bandwidth,
            'rolloff': rolloff
        }
    except:
        return {'centroid': 0, 'bandwidth': 0, 'rolloff': 0}


def voice_activity_detection(audio_segment, energy_threshold=None, min_speech_duration=None, use_adaptive=True):
    """
    Enhanced Voice Activity Detection (VAD) with adaptive noise floor and spectral analysis.
    
    Args:
        audio_segment: Audio segment to analyze
        energy_threshold: Minimum energy to consider as speech (None = use config)
        min_speech_duration: Minimum duration (ms) to consider as valid speech (None = use config)
        use_adaptive: Use adaptive noise floor estimation (default True)
    
    Returns:
        List of (start_ms, end_ms) tuples for speech segments
    """
    # Use config values if not explicitly provided
    if energy_threshold is None:
        energy_threshold = app_settings.vad_energy_threshold
    if min_speech_duration is None:
        min_speech_duration = app_settings.vad_min_speech_duration
    try:
        # Convert to numpy array
        audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        
        if len(audio_array) == 0:
            return []
        
        # Normalize audio
        if np.max(np.abs(audio_array)) > 0:
            audio_array = audio_array / np.max(np.abs(audio_array))
        
        # Estimate adaptive noise floor
        if use_adaptive:
            noise_floor = estimate_noise_floor(audio_array, audio_segment.frame_rate)
            # Set adaptive threshold: noise floor + margin
            adaptive_threshold = noise_floor + (energy_threshold * 0.3)  # 30% above noise floor
            effective_threshold = max(adaptive_threshold, energy_threshold * 0.7)  # At least 70% of config
        else:
            effective_threshold = energy_threshold
        
        # Calculate frame-based energy (50ms frames with 25ms overlap)
        frame_length = int(0.05 * audio_segment.frame_rate)  # 50ms
        hop_length = int(0.025 * audio_segment.frame_rate)   # 25ms
        
        speech_frames = []
        
        for i in range(0, len(audio_array) - frame_length, hop_length):
            frame = audio_array[i:i + frame_length]
            
            # Calculate RMS energy for this frame
            rms_energy = np.sqrt(np.mean(frame**2)) * 32767  # Scale back to int16 range
            
            # Calculate zero crossing rate (helps distinguish speech from noise)
            zcr = np.sum(np.diff(np.sign(frame)) != 0) / len(frame)
            
            # Calculate spectral features
            spectral = calculate_spectral_features(frame, audio_segment.frame_rate)
            
            # Enhanced speech detection criteria:
            # 1. Energy above adaptive threshold
            # 2. ZCR in typical speech range (0.01 to 0.3)
            # 3. Spectral centroid in speech range (300-3000 Hz)
            # 4. Spectral bandwidth indicates complex signal (not pure tone)
            # 5. Spectral rolloff in reasonable range
            
            energy_check = rms_energy > effective_threshold
            zcr_check = 0.01 < zcr < 0.3
            
            # Spectral checks to reject tonal noise (hum, airflow)
            centroid_check = 300 < spectral['centroid'] < 3500  # Speech frequency range
            bandwidth_check = spectral['bandwidth'] > 200  # Not a pure tone
            rolloff_check = spectral['rolloff'] < 4000  # Reasonable upper frequency
            
            # Combine criteria: energy + ZCR + at least 2 of 3 spectral checks
            spectral_score = sum([centroid_check, bandwidth_check, rolloff_check])
            
            is_speech = (
                energy_check and
                zcr_check and
                spectral_score >= 2  # At least 2 spectral features must pass
            )
            
            speech_frames.append(is_speech)
        
        # Convert frame-based detection to time segments
        speech_segments = []
        in_speech = False
        speech_start = 0
        
        for i, is_speech in enumerate(speech_frames):
            time_ms = i * hop_length / audio_segment.frame_rate * 1000
            
            if is_speech and not in_speech:
                # Start of speech
                speech_start = time_ms
                in_speech = True
            elif not is_speech and in_speech:
                # End of speech
                speech_duration = time_ms - speech_start
                if speech_duration >= min_speech_duration:
                    speech_segments.append((speech_start, time_ms))
                in_speech = False
        
        # Handle case where speech continues to end of audio
        if in_speech:
            final_time = len(audio_array) / audio_segment.frame_rate * 1000
            speech_duration = final_time - speech_start
            if speech_duration >= min_speech_duration:
                speech_segments.append((speech_start, final_time))
        
        return speech_segments
        
    except Exception as e:
        # Fallback to simple energy-based detection
        return simple_energy_vad(audio_segment, energy_threshold)

def simple_energy_vad(audio_segment, energy_threshold=1000):
    """
    Fallback VAD using simple energy thresholding.
    """
    try:
        # Use pydub's detect_nonsilent as fallback
        from pydub.silence import detect_nonsilent
        
        # Convert energy threshold to dBFS approximation
        dbfs_threshold = -40  # Conservative threshold
        
        speech_segments = detect_nonsilent(
            audio_segment,
            min_silence_len=200,  # 200ms minimum silence
            silence_thresh=dbfs_threshold
        )
        
        # Filter out very short segments (likely noise)
        filtered_segments = [
            (start, end) for start, end in speech_segments 
            if (end - start) >= 100  # At least 100ms
        ]
        
        return filtered_segments
        
    except:
        return []

# Releasing Detection - Agent never speaks (100% deterministic)
def releasing_detection(agent_segment, silence_thresh=None):
    """
    Returns 'Yes' if agent channel contains no speech events for entire call duration.
    
    Business Rules:
    - Analyze only the left channel (agent audio)
    - Apply robust VAD tuned to reject line noise, hum, static
    - Calls shorter than 4 seconds CANNOT be classified as releasing (insufficient duration)
    - If speech is detected, cannot be releasing regardless of call length
    - Must be 100% deterministic
    
    Args:
        agent_segment: Full audio segment (stereo or mono)
        silence_thresh: Optional silence threshold (unused, kept for compatibility)
    
    Returns:
        'Yes' if releasing, 'No' otherwise
    """
    
    # Extract left channel (agent audio only)
    agent_channel = extract_left_channel(agent_segment)
    
    # Get call duration in seconds
    call_duration_s = len(agent_channel) / 1000.0
    
    # Business Rule: Calls shorter than 4 seconds cannot be classified as releasing
    # Minimum duration required for reliable releasing detection
    MIN_DURATION_FOR_RELEASING = app_settings.late_hello_time  # Use same threshold (4-5s)
    
    if call_duration_s < MIN_DURATION_FOR_RELEASING:
        # Too short to determine releasing - classify as "No" (not releasing)
        return "No"
    
    # Apply Voice Activity Detection (uses config settings)
    speech_segments = voice_activity_detection(
        agent_channel,
        energy_threshold=app_settings.vad_energy_threshold,
        min_speech_duration=app_settings.vad_min_speech_duration,
        use_adaptive=True  # Use adaptive noise floor
    )
    
    # Releasing = NO speech events detected in entire call (and call is long enough)
    is_releasing = len(speech_segments) == 0
    
    return "Yes" if is_releasing else "No"

# Late Hello Detection - Agent first speaks after 4.0 seconds (100% deterministic)
def late_hello_detection(agent_segment, customer_segment=None):
    """
    Returns 'Yes' if first speech onset in agent channel occurs after 4.0 seconds from call start.
    
    Specification:
    - Analyze only the left channel (agent audio)
    - Timestamp speech onset with sub-second precision
    - If no speech occurs at all → falls under Releasing, not Late Hello
    - If speech starts ≤ 4.0s → no classification (normal)
    - Must be 100% deterministic
    """
    
    # Extract left channel (agent audio only)
    agent_channel = extract_left_channel(agent_segment)
    
    # Apply Voice Activity Detection to find all speech segments (uses config settings)
    speech_segments = voice_activity_detection(
        agent_channel,
        energy_threshold=app_settings.vad_energy_threshold,
        min_speech_duration=app_settings.vad_min_speech_duration,
        use_adaptive=True  # Use adaptive noise floor
    )
    
    # Edge case: No speech at all → falls under Releasing, not Late Hello
    if len(speech_segments) == 0:
        return "No"  # Not Late Hello (it's Releasing)
    
    # Find first speech onset time
    first_speech_start_ms = speech_segments[0][0]  # Start time of first speech segment
    
    # Late Hello threshold: configurable (default 5.0 seconds)
    late_hello_threshold_ms = app_settings.late_hello_time * 1000.0
    
    # Late Hello = first speech onset occurs AFTER 4.0 seconds
    is_late_hello = first_speech_start_ms > late_hello_threshold_ms
    
    return "Yes" if is_late_hello else "No"


# Debug function to analyze audio characteristics with new VAD logic
def debug_audio_analysis(agent_segment, file_name="Unknown"):
    """
    Analyze audio segment and return detailed information for debugging.
    Uses the same VAD logic as the detection functions.
    """
    try:
        # Extract left channel (agent audio)
        agent_channel = extract_left_channel(agent_segment)
        
        # Basic info
        duration_ms = len(agent_channel)
        duration_s = duration_ms / 1000.0
        channels = agent_segment.channels
        
        # dBFS analysis
        dbfs = agent_channel.dBFS
        
        # Apply VAD to find speech segments (uses config settings)
        speech_segments = voice_activity_detection(
            agent_channel,
            energy_threshold=app_settings.vad_energy_threshold,
            min_speech_duration=app_settings.vad_min_speech_duration,
            use_adaptive=True  # Use adaptive noise floor
        )
        
        # Calculate speech statistics
        total_speech_duration = sum([end - start for start, end in speech_segments])
        speech_percentage = (total_speech_duration / duration_ms) if duration_ms > 0 else 0
        
        # First speech onset time
        first_speech_onset = speech_segments[0][0] if speech_segments else None
        first_speech_onset_s = first_speech_onset / 1000.0 if first_speech_onset is not None else None
        
        # Energy analysis
        audio_array = np.array(agent_channel.get_array_of_samples())
        if len(audio_array) > 0:
            rms_energy = np.sqrt(np.mean(audio_array**2))
            peak_energy = np.max(np.abs(audio_array))
        else:
            rms_energy = peak_energy = 0
        
        # Detection results
        releasing_result = releasing_detection(agent_segment)
        late_hello_result = late_hello_detection(agent_segment)
        
        return {
            "file_name": file_name,
            "duration_seconds": round(duration_s, 2),
            "channels": channels,
            "dbfs": round(dbfs, 2) if dbfs != float('-inf') else "Silent",
            "rms_energy": round(rms_energy, 2),
            "peak_energy": round(peak_energy, 2),
            "speech_segments_count": len(speech_segments),
            "total_speech_duration_ms": round(total_speech_duration, 1),
            "speech_percentage": round(speech_percentage * 100, 1),
            "first_speech_onset_ms": round(first_speech_onset, 1) if first_speech_onset else "None",
            "first_speech_onset_s": round(first_speech_onset_s, 3) if first_speech_onset_s else "None",
            "releasing_detection": releasing_result,
            "late_hello_detection": late_hello_result,
            "speech_segments": [(round(start, 1), round(end, 1)) for start, end in speech_segments[:5]]  # First 5 segments
        }
    except Exception as e:
        return {
            "file_name": file_name,
            "error": str(e),
            "releasing_detection": "Error",
            "late_hello_detection": "Error"
        }
 
 
 