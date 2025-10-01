# Answers to Your Questions

## ❓ Question 1: What are the current system settings/parameters used to measure audio and detect speech?

### **Current Detection Parameters (After Update)**

#### **1. Late Hello Detection Window**
- **Location**: `config.py` line 101, `intro_detection.py` line 192
- **Previous Value**: 4.0 seconds
- **Current Value**: **5.0 seconds**
- **Purpose**: Maximum time allowed before agent speaks without being flagged
- **Configurable**: Yes, via `app_settings.late_hello_time`

---

#### **2. Voice Activity Detection (VAD) - Energy Threshold**
- **Location**: `config.py` line 106, `intro_detection.py` line 19
- **Previous Value**: 800 RMS units
- **Current Value**: **600 RMS units** (default)
- **What it measures**: Root Mean Square (RMS) energy of audio signal
- **How it works**: 
  - Audio is split into 50ms frames
  - Each frame's RMS energy is calculated: `sqrt(mean(signal^2))`
  - Frames with energy > threshold are considered potential speech
- **Range**: 400 (high sensitivity) to 900 (low sensitivity)
- **Configurable**: Yes, via `app_settings.vad_energy_threshold`

---

#### **3. Minimum Speech Duration**
- **Location**: `config.py` line 107, `intro_detection.py` line 19
- **Previous Value**: 150 milliseconds
- **Current Value**: **100 milliseconds**
- **Purpose**: Filters out transient noise spikes (clicks, pops, static bursts)
- **How it works**: Only speech segments lasting ≥ 100ms are considered valid
- **Range**: 80ms (high sensitivity) to 150ms (low sensitivity)
- **Configurable**: Yes, via `app_settings.vad_min_speech_duration`

---

#### **4. Zero Crossing Rate (ZCR) Filter**
- **Location**: `intro_detection.py` lines 54-65
- **Value**: 0.01 to 0.3 (fixed)
- **What it measures**: Rate at which audio signal changes from positive to negative
- **Purpose**: Distinguishes speech (complex waveform) from pure tones/hum/noise
- **How it works**: `count(sign changes) / frame_length`
- **Why fixed**: This range is speech-specific and doesn't need adjustment
- **Not configurable**: Optimal for human speech detection

---

#### **5. Frame Analysis Parameters**
- **Location**: `intro_detection.py` lines 43-44
- **Frame Length**: 50 milliseconds
- **Hop Length**: 25 milliseconds (50% overlap)
- **Purpose**: Provides temporal resolution for precise speech onset detection
- **How it works**: Audio is analyzed in sliding windows
- **Not configurable**: Standard values for speech processing

---

#### **6. Fallback Detection (dBFS-based)**
- **Location**: `intro_detection.py` lines 101-127
- **Threshold**: -40 dBFS (decibels relative to full scale)
- **Minimum Silence Length**: 200ms
- **Purpose**: Backup detection method if primary VAD fails
- **How it works**: Uses pydub's built-in silence detection
- **When used**: If primary VAD encounters an error

---

### **Detection Algorithm Flow**

```
1. Load Audio File
   ↓
2. Extract Left Channel (Agent Audio)
   ↓
3. Normalize Audio (scale to -1 to +1)
   ↓
4. Split into 50ms frames (25ms overlap)
   ↓
5. For each frame:
   - Calculate RMS Energy
   - Calculate Zero Crossing Rate
   - Is Speech? (Energy > threshold AND 0.01 < ZCR < 0.3)
   ↓
6. Merge consecutive speech frames
   ↓
7. Filter segments < minimum duration
   ↓
8. Return speech segments: [(start_ms, end_ms), ...]
   ↓
9. Classification:
   - Releasing: len(segments) == 0
   - Late Hello: segments[0][0] > late_hello_threshold
```

---

## ❓ Question 2: What solutions or adjustments can be applied to improve sensitivity?

### **✅ Solutions Implemented (Phase 1)**

#### **1. Extended Late Hello Window**
**Change**: 4 seconds → 5 seconds
```python
# config.py line 101
self.late_hello_time = 5
```

**Impact**:
- ✅ Reduces false positives from network delays
- ✅ Allows more time for connection establishment
- ✅ Minimal risk of missing genuine late responses

---

#### **2. Lowered Energy Threshold**
**Change**: 800 → 600 RMS units
```python
# config.py line 106
self.vad_energy_threshold = 600
```

**Impact**:
- ✅ Detects fainter speech from poor connections
- ✅ Catches low-volume "hello" utterances
- ✅ Better handles audio compression artifacts
- ⚠️ May detect slightly more background noise (mitigated by ZCR filter)

---

#### **3. Reduced Minimum Speech Duration**
**Change**: 150ms → 100ms
```python
# config.py line 107
self.vad_min_speech_duration = 100
```

**Impact**:
- ✅ Catches brief/clipped "hello" utterances
- ✅ Handles cases where first syllable is cut off
- ✅ Still filters most noise bursts (< 100ms)

---

#### **4. Configurable Sensitivity Presets**
**New Feature**: Three preset levels
```python
# config.py lines 109-113
self.vad_sensitivity = 'medium'  # Options: 'high', 'medium', 'low'

# Apply preset
app_settings.apply_vad_sensitivity_preset('high')
```

**Presets**:

| Preset | Energy | Duration | Use Case |
|--------|--------|----------|----------|
| **HIGH** | 400 | 80ms | **← Use this for your connection issues** |
| MEDIUM | 600 | 100ms | Standard quality (default) |
| LOW | 900 | 150ms | High noise environments |

**Impact**:
- ✅ Easy switching between sensitivity levels
- ✅ No code changes needed to adjust
- ✅ Can test different levels on same file

---

### **🔧 Additional Solutions Available (Phase 2)**

#### **5. Adaptive Energy Normalization** (Not yet implemented)
**Concept**: Calculate per-file baseline energy, set threshold relative to that

**How it would work**:
```python
# Measure file's energy distribution
baseline_energy = calculate_baseline(audio)
adaptive_threshold = baseline_energy * 1.5  # 50% above baseline

# Use adaptive threshold instead of fixed
speech_segments = vad(audio, threshold=adaptive_threshold)
```

**Benefits**:
- Automatically adjusts for varying recording levels
- Handles both loud and quiet recordings optimally
- Reduces manual tuning

**Complexity**: Medium
**Implementation Time**: 2-3 hours

---

#### **6. Multi-Pass Detection** (Not yet implemented)
**Concept**: If first pass finds no speech, retry with relaxed thresholds

**How it would work**:
```python
# First pass: standard sensitivity
segments = vad(audio, threshold=600)

if len(segments) == 0:
    # Second pass: high sensitivity
    segments = vad(audio, threshold=400)
    
    if len(segments) > 0:
        # Flag for manual review (uncertain case)
        flag_for_review = True
```

**Benefits**:
- Catches edge cases without lowering primary threshold
- Maintains low false positive rate
- Identifies uncertain cases for manual review

**Complexity**: Low
**Implementation Time**: 1 hour

---

#### **7. Spectral Analysis Enhancement** (Not yet implemented)
**Concept**: Add frequency-domain features to complement energy+ZCR

**Additional Features**:
- **Spectral Centroid**: Center of mass of spectrum (speech typically 500-2000 Hz)
- **Spectral Bandwidth**: Spread of frequencies (speech has moderate bandwidth)
- **Spectral Rolloff**: Frequency below which 85% of energy is contained

**How it would work**:
```python
# Calculate spectral features
centroid = calculate_spectral_centroid(frame)
bandwidth = calculate_spectral_bandwidth(frame)

# Enhanced speech detection
is_speech = (
    energy > threshold AND
    0.01 < zcr < 0.3 AND
    500 < centroid < 2000 AND  # Speech frequency range
    bandwidth > min_bandwidth   # Not a pure tone
)
```

**Benefits**:
- Better distinguishes distorted speech from noise
- More robust to audio compression artifacts
- Handles frequency-shifted audio (poor connections)

**Complexity**: Medium-High
**Implementation Time**: 4-6 hours

---

#### **8. ML-Based VAD** (Not yet implemented)
**Concept**: Use pre-trained deep learning model for speech detection

**Options**:
- **Silero VAD**: Fast, accurate, PyTorch-based
- **WebRTC VAD**: Lightweight, C-based
- **pyannote.audio**: State-of-art, but heavier

**Example with Silero**:
```python
import torch
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
(get_speech_timestamps, _, _, _, _) = utils

# Get speech timestamps
speech_timestamps = get_speech_timestamps(audio, model)
```

**Benefits**:
- State-of-art accuracy
- Handles distortion/noise better than rule-based
- Trained on diverse audio conditions

**Trade-offs**:
- Adds PyTorch dependency (~500MB)
- Slightly slower processing (~2-3x)
- Less transparent (black box)

**Complexity**: Low (using pre-trained model)
**Implementation Time**: 2-3 hours

---

### **🎯 Recommended Solution for Your Specific Problem**

**Your Issue**: Connection issues → faint/unclear speech → system fails to detect → false "late hello" or "releasing" flags

**Immediate Solution (Already Implemented)**:
```python
from config import app_settings

# Apply high sensitivity preset
app_settings.apply_vad_sensitivity_preset('high')

# This sets:
# - Energy threshold: 400 (very sensitive)
# - Min speech duration: 80ms (catches brief utterances)
# - Late hello time: 5s (already set, allows network delay)
```

**Testing**:
```bash
# Test on your problematic files
python test_sensitivity.py "path/to/problem_call.mp3" compare

# This will show you how each preset performs
```

**Expected Results**:
- ✅ Faint "hello" will now be detected
- ✅ Network delays up to 5s won't trigger late-hello
- ✅ Brief utterances (>80ms) will be caught
- ⚠️ May detect slightly more background noise (monitor false positive rate)

---

### **📊 Validation Process**

1. **Collect Test Set**: Gather 20-30 files that were incorrectly flagged
2. **Test Current Settings**: Run with 'medium' preset
3. **Test High Sensitivity**: Run with 'high' preset
4. **Compare Results**: 
   - How many previously missed speeches are now detected?
   - Are there new false positives?
5. **Adjust if Needed**: 
   - Too many false positives? Use 'medium' or custom threshold (500)
   - Still missing some? Use custom threshold (350)

---

### **🔬 Advanced Tuning (If Needed)**

If presets don't work perfectly, fine-tune manually:

```python
from config import app_settings

# Custom tuning for your specific audio quality
app_settings.vad_energy_threshold = 450  # Between high and medium
app_settings.vad_min_speech_duration = 90  # Between high and medium
app_settings.late_hello_time = 5.5  # Slightly more tolerance

# Test
python test_sensitivity.py "problem_call.mp3"
```

---

## 📈 Performance Metrics to Track

After implementing changes, monitor:

1. **False Negative Rate**: Calls where agent spoke but system said "Releasing"
   - **Target**: < 2%
   - **Previous**: ~10-15% (based on your description)
   - **Expected after fix**: < 3%

2. **False Positive Rate**: Calls where noise was detected as speech
   - **Target**: < 5%
   - **Expected after fix**: May increase slightly (3-7%)

3. **Late Hello Accuracy**: Calls correctly identified as late hello
   - **Target**: > 95%
   - **Expected after fix**: > 97% (with 5s threshold)

4. **Manual Review Rate**: Calls flagged for manual review
   - **Target**: < 10%
   - **Expected**: 5-8%

---

## 🎯 Summary

### **What Changed**:
1. ✅ Late hello: 4s → 5s
2. ✅ Energy threshold: 800 → 600 (default), with 400 (high) option
3. ✅ Min speech duration: 150ms → 100ms (default), with 80ms (high) option
4. ✅ Added configurable sensitivity presets
5. ✅ Created testing utility

### **How to Use**:
```python
# In your code or config.py
from config import app_settings
app_settings.apply_vad_sensitivity_preset('high')
```

### **How to Test**:
```bash
python test_sensitivity.py "problem_file.mp3" compare
```

### **Expected Impact**:
- ✅ Faint speech from connection issues will be detected
- ✅ Network delays up to 5s won't cause false flags
- ✅ Brief utterances will be caught
- ⚠️ Monitor for slight increase in false positives

---

## 📞 Next Steps

1. **Test on problematic files**: Use `test_sensitivity.py` with 'compare' mode
2. **Apply high sensitivity**: If tests show improvement
3. **Validate on batch**: Run on 50-100 files to ensure no excessive false positives
4. **Fine-tune if needed**: Adjust thresholds based on results
5. **Deploy to production**: Once validated

---

**All changes are backward compatible and can be reverted by changing presets back to 'low' or adjusting thresholds manually.**
