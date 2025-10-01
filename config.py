# ==================== config.py ====================
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# ────────────── Base directories ──────────────
BASE_DIR        = Path(__file__).parent
RECORDINGS_DIR  = BASE_DIR / "Recordings"

# Ensure directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# ────────────── ReadyMode Dialer URLs ──────────────
READY_MODE_URLS = {
    "default": "https://resva.readymode.com/",
    "resva":    "https://resva.readymode.com/",
    "resva2":   "https://resva2.readymode.com/",
    "resva4":   "https://resva4.readymode.com/",
    "resva5":   "https://resva5.readymode.com/",
    "resva6":   "https://resva6.readymode.com/",
    "resva7":   "https://resva7.readymode.com/",
    "gfcl":     "https://gfcl.readymode.com/",
}

# ────────────── Download directory alias ──────────────
READYMODE_URL = READY_MODE_URLS["default"]

# ────────────── Speech Recognition Configuration ──────────────
# Accent adaptation settings
ACCENT = os.getenv("ACCENT", "egyptian")  # Options: "standard", "egyptian"

# Whisper model configuration - Use tiny for faster processing
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")  # Options: "tiny", "base", "small", "medium", "large"
SAMPLE_RATE = 16000  # Hz - Whisper expects 16kHz audio
LANGUAGE = "en"  # Primary language for transcription

# Egyptian English accent prompt for Whisper
EGYPTIAN_ENGLISH_PROMPT = (
    "This conversation features Egyptian-accented English. "
    "Typical characteristics include pronunciation shifts such as 'th' becoming 's' or 'd', "
    "elongated vowels, and altered stress patterns. "
    "Examples: 'dis' instead of 'this', 'tink' instead of 'think', 'ze' instead of 'the'. "
    "The model should adapt to these patterns for improved recognition accuracy."
)

# User credentials for authentication
USER_CREDENTIALS = {
    'auditor1': 'res-2045',
    'auditor2': 'res-3821',
    'auditor3': 'res-6592',
    'auditor4': 'res-7130',
    'auditor5': 'res-1897',
    'auditor6': 'res-4783',
    'auditor7': 'res-9264',
    # Add more users here if needed:
    # 'username': 'password',
}

# ────────────── Settings Singleton ──────────────
class AppSettings:
    """
    Centralized settings management for all analysis parameters.
    This singleton ensures all backend functions use the same settings.
    """
    def __init__(self):
        # Sound level thresholds (dBFS)
        self.sound_perfect = -26.0
        self.sound_good = -27.5
        self.sound_low = -29.0
        
        # Network issue detection thresholds
        self.rolloff_thresh = 0.85
        self.zcr_diff_thresh = 0.25
        self.amp_cv_thresh = 0.7
        self.frag_count_thresh = 3
        
        # Silence detection parameters
        self.min_silence_len = 200
        self.silence_thresh = -40
        self.cutting_perfect_max = 1
        self.cutting_good_max = 3
        
        # Tonality parameters (dBFS-based)
        self.tonality_perfect = -20   # dBFS
        self.tonality_good = -25      # dBFS
        self.tonality_low = -30       # dBFS
        
        # Introduction phrases
        self.intro_phrases = "my name is,this is,i am,i'm"
        self.purpose_phrases = "property,calling about,regarding,reaching out,house,the one at"
        
        # Energy threshold
        self.energy_thresh = -32
        
        # Red flag override
        self.silent_thresh = -45
        self.silent_duration = 4000

        # Late hello detection time (in seconds)
        self.late_hello_time = 5  # Extended to 5 seconds for network delay tolerance
        
        # Voice Activity Detection (VAD) sensitivity settings
        # Lower values = more sensitive (detects fainter speech)
        # Higher values = less sensitive (rejects more noise)
        self.vad_energy_threshold = 600  # RMS energy threshold (default: 600, was 800)
        self.vad_min_speech_duration = 100  # Minimum speech duration in ms (default: 100, was 150)
        
        # Sensitivity presets for easy adjustment
        # 'high' = detects faint/unclear speech (more false positives)
        # 'medium' = balanced detection (recommended)
        # 'low' = only clear speech (more false negatives)
        self.vad_sensitivity = 'medium'  # Options: 'high', 'medium', 'low'
        
    def update_from_ui(self, ui_settings):
        """
        Update settings from UI values.
        
        Args:
            ui_settings: Dict of setting_name -> value pairs
        """
        for key, value in ui_settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
                print(f"Updated setting: {key} = {value}")
    
    def get_sound_thresholds(self):
        """Get sound level thresholds as tuple."""
        return self.sound_perfect, self.sound_good, self.sound_low
    
    def get_network_thresholds(self):
        """Get network detection thresholds as tuple."""
        return self.rolloff_thresh, self.zcr_diff_thresh, self.amp_cv_thresh, self.frag_count_thresh
    
    def get_silence_thresholds(self):
        """Get silence detection thresholds as tuple."""
        return self.min_silence_len, self.silence_thresh, self.cutting_perfect_max, self.cutting_good_max
    
    def get_tonality_thresholds(self):
        """Get tonality thresholds as tuple."""
        return self.tonality_perfect, self.tonality_good, self.tonality_low
    
    def get_intro_phrases(self):
        """Get introduction phrases as list."""
        return [p.strip() for p in self.intro_phrases.split(",")]
    
    def get_purpose_phrases(self):
        """Get purpose phrases as list."""
        return [p.strip() for p in self.purpose_phrases.split(",")]
    
    def apply_vad_sensitivity_preset(self, preset='medium'):
        """
        Apply VAD sensitivity preset.
        
        Args:
            preset: 'high', 'medium', or 'low'
        """
        presets = {
            'high': {
                'vad_energy_threshold': 400,  # Very sensitive - catches faint speech
                'vad_min_speech_duration': 80,  # Shorter minimum duration
                'description': 'High sensitivity - detects faint/unclear speech (may have more false positives)'
            },
            'medium': {
                'vad_energy_threshold': 600,  # Balanced sensitivity
                'vad_min_speech_duration': 100,  # Standard minimum duration
                'description': 'Medium sensitivity - balanced detection (recommended)'
            },
            'low': {
                'vad_energy_threshold': 900,  # Less sensitive - only clear speech
                'vad_min_speech_duration': 150,  # Longer minimum duration
                'description': 'Low sensitivity - only clear speech (may miss faint audio)'
            }
        }
        
        if preset not in presets:
            print(f"⚠️ Invalid preset '{preset}'. Using 'medium'.")
            preset = 'medium'
        
        config = presets[preset]
        self.vad_energy_threshold = config['vad_energy_threshold']
        self.vad_min_speech_duration = config['vad_min_speech_duration']
        self.vad_sensitivity = preset
        
        print(f"✅ VAD Sensitivity: {preset.upper()}")
        print(f"   Energy Threshold: {self.vad_energy_threshold}")
        print(f"   Min Speech Duration: {self.vad_min_speech_duration}ms")
        print(f"   {config['description']}")
    
    def get_vad_parameters(self):
        """Get current VAD parameters as tuple."""
        return self.vad_energy_threshold, self.vad_min_speech_duration

# Global settings instance
app_settings = AppSettings()



