"""
Test script to debug Late Hello detection on specific audio files
This will show you exactly when the agent first speaks and why it's being classified
"""

import sys
from pathlib import Path
from pydub import AudioSegment
from analyzer.intro_detection import late_hello_detection, extract_left_channel, voice_activity_detection
from config import app_settings

def test_late_hello(audio_file_path):
    """
    Test late hello detection on a specific audio file with detailed debug output.
    
    Args:
        audio_file_path: Path to the MP3/WAV file to test
    """
    file_path = Path(audio_file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print("=" * 70)
    print(f"LATE HELLO DEBUG TEST")
    print("=" * 70)
    print(f"File: {file_path.name}")
    print(f"Late Hello Threshold: {app_settings.late_hello_time} seconds")
    print(f"VAD Energy Threshold: {app_settings.vad_energy_threshold}")
    print(f"VAD Min Speech Duration: {app_settings.vad_min_speech_duration}ms")
    print("=" * 70)
    
    # Load audio
    print("\n📂 Loading audio file...")
    audio = AudioSegment.from_file(str(file_path))
    print(f"   Duration: {len(audio)/1000:.2f} seconds")
    print(f"   Channels: {audio.channels}")
    print(f"   Sample Rate: {audio.frame_rate} Hz")
    
    # Extract agent channel
    print("\n🎤 Extracting agent channel (left)...")
    agent_channel = extract_left_channel(audio)
    
    # Get speech segments
    print("\n🔍 Detecting speech segments...")
    speech_segments = voice_activity_detection(
        agent_channel,
        energy_threshold=app_settings.vad_energy_threshold,
        min_speech_duration=app_settings.vad_min_speech_duration,
        use_adaptive=True
    )
    
    print(f"   Found {len(speech_segments)} speech segment(s)")
    
    if len(speech_segments) == 0:
        print("\n⚠️ NO SPEECH DETECTED!")
        print("   This would be classified as 'Releasing', not 'Late Hello'")
        print("\n💡 Possible reasons:")
        print("   1. Audio is too quiet (below VAD threshold)")
        print("   2. Only background noise present")
        print("   3. VAD sensitivity too low")
        print(f"\n   Try lowering VAD energy threshold (current: {app_settings.vad_energy_threshold})")
    else:
        print("\n📊 Speech Segments (first 10):")
        print("   " + "-" * 60)
        for i, (start_ms, end_ms) in enumerate(speech_segments[:10], 1):
            start_s = start_ms / 1000.0
            end_s = end_ms / 1000.0
            duration_s = (end_ms - start_ms) / 1000.0
            print(f"   {i:2d}. {start_s:6.2f}s - {end_s:6.2f}s  (duration: {duration_s:.2f}s)")
        if len(speech_segments) > 10:
            print(f"   ... and {len(speech_segments) - 10} more segments")
        print("   " + "-" * 60)
        
        # First speech analysis
        first_speech_start_ms = speech_segments[0][0]
        first_speech_start_s = first_speech_start_ms / 1000.0
        
        print(f"\n⏱️  FIRST SPEECH ONSET:")
        print(f"   Time: {first_speech_start_s:.2f} seconds ({first_speech_start_ms:.0f}ms)")
        print(f"   Threshold: {app_settings.late_hello_time} seconds ({app_settings.late_hello_time * 1000:.0f}ms)")
        
        if first_speech_start_s > app_settings.late_hello_time:
            print(f"\n❌ LATE HELLO DETECTED!")
            print(f"   Agent spoke at {first_speech_start_s:.2f}s, which is AFTER {app_settings.late_hello_time}s threshold")
        else:
            print(f"\n✅ NORMAL (On Time)")
            print(f"   Agent spoke at {first_speech_start_s:.2f}s, which is BEFORE {app_settings.late_hello_time}s threshold")
    
    # Run actual detection with debug
    print("\n" + "=" * 70)
    print("RUNNING LATE_HELLO_DETECTION() WITH DEBUG:")
    print("=" * 70)
    result = late_hello_detection(audio, debug=True)
    
    print(f"\n" + "=" * 70)
    print(f"FINAL RESULT: {result}")
    print("=" * 70)
    
    # Recommendations
    if result == "Yes" and len(speech_segments) > 0:
        first_speech_s = speech_segments[0][0] / 1000.0
        if first_speech_s < 5.0:
            print("\n⚠️ WARNING: Speech detected before 5s but still marked as Late Hello!")
            print("   This might be a bug. Speech was detected at {:.2f}s".format(first_speech_s))
            print("\n💡 Possible causes:")
            print("   1. VAD is detecting noise as speech before actual speech")
            print("   2. Try increasing VAD energy threshold to ignore early noise")
            print(f"   3. Current threshold: {app_settings.vad_energy_threshold} (try 700-800)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_late_hello_debug.py <path_to_audio_file>")
        print("\nExample:")
        print('  python test_late_hello_debug.py "Recordings/Agent/user/agent_123.mp3"')
        sys.exit(1)
    
    audio_file = sys.argv[1]
    test_late_hello(audio_file)
