"""
VAD Sensitivity Testing Utility

This script helps you test and adjust Voice Activity Detection (VAD) sensitivity
on problematic audio files to find optimal settings.

Usage:
    python test_sensitivity.py <audio_file_path> [sensitivity_preset]
    
    sensitivity_preset: 'high', 'medium', or 'low' (default: 'medium')

Example:
    python test_sensitivity.py "Recordings/Agent/test_call.mp3" high
"""

import sys
from pathlib import Path
from pydub import AudioSegment
from config import app_settings
from analyzer.intro_detection import (
    extract_left_channel,
    voice_activity_detection,
    releasing_detection,
    late_hello_detection,
    debug_audio_analysis
)


def test_audio_with_sensitivity(audio_path, sensitivity='medium'):
    """
    Test audio file with specified sensitivity preset.
    
    Args:
        audio_path: Path to audio file
        sensitivity: 'high', 'medium', or 'low'
    """
    print("=" * 80)
    print(f"🎯 VAD SENSITIVITY TEST")
    print("=" * 80)
    print(f"📁 File: {audio_path}")
    print()
    
    # Apply sensitivity preset
    app_settings.apply_vad_sensitivity_preset(sensitivity)
    print()
    
    # Load audio
    try:
        audio = AudioSegment.from_file(audio_path)
        print(f"✅ Audio loaded successfully")
        print(f"   Duration: {len(audio) / 1000:.2f} seconds")
        print(f"   Channels: {audio.channels}")
        print(f"   Sample Rate: {audio.frame_rate} Hz")
        print()
    except Exception as e:
        print(f"❌ Failed to load audio: {e}")
        return
    
    # Extract agent channel
    agent_channel = extract_left_channel(audio)
    
    # Run VAD with current settings
    print("🔍 Running Voice Activity Detection...")
    print(f"   Energy Threshold: {app_settings.vad_energy_threshold}")
    print(f"   Min Speech Duration: {app_settings.vad_min_speech_duration}ms")
    print()
    
    speech_segments = voice_activity_detection(
        agent_channel,
        energy_threshold=app_settings.vad_energy_threshold,
        min_speech_duration=app_settings.vad_min_speech_duration
    )
    
    # Display results
    print("📊 DETECTION RESULTS")
    print("-" * 80)
    print(f"Speech Segments Found: {len(speech_segments)}")
    
    if speech_segments:
        print(f"\nFirst 10 Speech Segments:")
        for i, (start, end) in enumerate(speech_segments[:10], 1):
            duration = end - start
            print(f"  {i}. {start/1000:.3f}s - {end/1000:.3f}s (duration: {duration:.0f}ms)")
        
        first_speech_time = speech_segments[0][0] / 1000.0
        print(f"\n⏱️  First Speech Onset: {first_speech_time:.3f} seconds")
    else:
        print("  ⚠️  No speech detected!")
    
    print()
    
    # Run classification
    print("🏷️  CLASSIFICATION")
    print("-" * 80)
    
    releasing = releasing_detection(audio)
    late_hello = late_hello_detection(audio)
    
    print(f"Releasing Detection: {releasing}")
    print(f"Late Hello Detection: {late_hello} (threshold: {app_settings.late_hello_time}s)")
    print()
    
    # Detailed debug analysis
    print("🔬 DETAILED AUDIO ANALYSIS")
    print("-" * 80)
    debug_info = debug_audio_analysis(audio, Path(audio_path).name)
    
    for key, value in debug_info.items():
        if key not in ['file_name', 'speech_segments']:
            print(f"{key}: {value}")
    
    print()
    print("=" * 80)


def compare_sensitivities(audio_path):
    """
    Compare detection results across all sensitivity presets.
    
    Args:
        audio_path: Path to audio file
    """
    print("=" * 80)
    print(f"🔬 SENSITIVITY COMPARISON")
    print("=" * 80)
    print(f"📁 File: {audio_path}")
    print()
    
    # Load audio once
    try:
        audio = AudioSegment.from_file(audio_path)
        agent_channel = extract_left_channel(audio)
    except Exception as e:
        print(f"❌ Failed to load audio: {e}")
        return
    
    results = []
    
    for sensitivity in ['low', 'medium', 'high']:
        print(f"\n{'─' * 80}")
        print(f"Testing: {sensitivity.upper()} Sensitivity")
        print('─' * 80)
        
        # Apply preset
        app_settings.apply_vad_sensitivity_preset(sensitivity)
        
        # Run detection
        speech_segments = voice_activity_detection(
            agent_channel,
            energy_threshold=app_settings.vad_energy_threshold,
            min_speech_duration=app_settings.vad_min_speech_duration
        )
        
        releasing = releasing_detection(audio)
        late_hello = late_hello_detection(audio)
        
        first_speech = speech_segments[0][0] / 1000.0 if speech_segments else None
        
        results.append({
            'sensitivity': sensitivity,
            'segments_found': len(speech_segments),
            'first_speech': first_speech,
            'releasing': releasing,
            'late_hello': late_hello
        })
        
        print(f"  Segments Found: {len(speech_segments)}")
        print(f"  First Speech: {first_speech:.3f}s" if first_speech else "  First Speech: None")
        print(f"  Releasing: {releasing}")
        print(f"  Late Hello: {late_hello}")
    
    # Summary table
    print("\n" + "=" * 80)
    print("📊 COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Sensitivity':<15} {'Segments':<12} {'First Speech':<15} {'Releasing':<12} {'Late Hello'}")
    print("-" * 80)
    
    for r in results:
        first_speech_str = f"{r['first_speech']:.3f}s" if r['first_speech'] else "None"
        print(f"{r['sensitivity'].upper():<15} {r['segments_found']:<12} {first_speech_str:<15} {r['releasing']:<12} {r['late_hello']}")
    
    print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    if not Path(audio_path).exists():
        print(f"❌ File not found: {audio_path}")
        sys.exit(1)
    
    # Check if comparison mode
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'compare':
        compare_sensitivities(audio_path)
    else:
        sensitivity = sys.argv[2] if len(sys.argv) > 2 else 'medium'
        test_audio_with_sensitivity(audio_path, sensitivity)
        
        # Suggest comparison
        print("\n💡 TIP: Run with 'compare' argument to test all sensitivity levels:")
        print(f"   python test_sensitivity.py \"{audio_path}\" compare")


if __name__ == "__main__":
    main()
