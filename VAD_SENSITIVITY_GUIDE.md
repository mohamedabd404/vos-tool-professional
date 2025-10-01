# VAD Sensitivity Configuration Guide

## 🎯 Overview

This guide explains the Voice Activity Detection (VAD) sensitivity system and how to adjust it for optimal performance with varying audio quality.

---

## 📊 Current System Parameters

### **Late Hello Detection Window**
- **Previous**: 4.0 seconds
- **Current**: 5.0 seconds
- **Rationale**: Provides tolerance for network delays and connection issues

### **Voice Activity Detection (VAD) Parameters**

#### **Energy Threshold**
- **What it measures**: RMS (Root Mean Square) energy of audio signal
- **Purpose**: Distinguishes speech from background noise
- **Previous value**: 800
- **Current default**: 600
- **Range**: 400 (high sensitivity) to 900 (low sensitivity)

#### **Minimum Speech Duration**
- **What it measures**: Minimum duration for valid speech segment
- **Purpose**: Filters out transient noise spikes
- **Previous value**: 150ms
- **Current default**: 100ms
- **Range**: 80ms (high sensitivity) to 150ms (low sensitivity)

#### **Zero Crossing Rate (ZCR)**
- **What it measures**: Rate at which signal changes sign
- **Purpose**: Distinguishes speech from pure noise/hum
- **Value**: 0.01 to 0.3 (fixed, optimal for speech)
- **Note**: This parameter is not user-configurable as it's speech-specific

#### **Frame Analysis**
- **Frame Length**: 50ms windows
- **Hop Length**: 25ms overlap
- **Purpose**: Provides temporal resolution for speech detection

---

## 🎚️ Sensitivity Presets

### **HIGH Sensitivity**
```python
Energy Threshold: 400
Min Speech Duration: 80ms
```

**Use when:**
- Poor network quality calls
- Low volume recordings
- Faint or unclear speech
- Background noise is minimal

**Trade-offs:**
- ✅ Catches faint speech that would otherwise be missed
- ✅ Better for connection-issue scenarios
- ⚠️ May detect more background noise as speech
- ⚠️ Slightly higher false positive rate

---

### **MEDIUM Sensitivity** (Recommended Default)
```python
Energy Threshold: 600
Min Speech Duration: 100ms
```

**Use when:**
- Normal audio quality
- Standard call center recordings
- Balanced detection needed

**Trade-offs:**
- ✅ Balanced false positive/negative rates
- ✅ Works well for most scenarios
- ✅ Filters most background noise

---

### **LOW Sensitivity**
```python
Energy Threshold: 900
Min Speech Duration: 150ms
```

**Use when:**
- High background noise environment
- Need to minimize false positives
- Only want to detect clear, strong speech

**Trade-offs:**
- ✅ Very low false positive rate
- ✅ Only detects clear speech
- ⚠️ May miss faint or unclear speech
- ⚠️ Higher false negative rate on poor quality audio

---

## 🔧 How to Adjust Sensitivity

### **Method 1: Using Presets (Recommended)**

Edit `config.py`:

```python
# In AppSettings.__init__()
self.vad_sensitivity = 'high'  # Options: 'high', 'medium', 'low'
```

Then apply the preset in your code:

```python
from config import app_settings

# Apply preset
app_settings.apply_vad_sensitivity_preset('high')
```

---

### **Method 2: Manual Fine-Tuning**

Edit `config.py` directly:

```python
# In AppSettings.__init__()
self.vad_energy_threshold = 500  # Custom value
self.vad_min_speech_duration = 90  # Custom value (ms)
```

---

### **Method 3: Runtime Adjustment**

```python
from config import app_settings

# Adjust at runtime
app_settings.vad_energy_threshold = 550
app_settings.vad_min_speech_duration = 95
```

---

## 🧪 Testing Your Settings

### **Test Single File**

```bash
python test_sensitivity.py "path/to/audio.mp3" medium
```

### **Compare All Presets**

```bash
python test_sensitivity.py "path/to/audio.mp3" compare
```

This will show you how each sensitivity level performs on your problematic files.

---

## 📈 Optimization Workflow

### **Step 1: Identify Problem Files**
Collect audio files that are being incorrectly flagged:
- False positives (agent spoke but not detected)
- False negatives (noise detected as speech)

### **Step 2: Test Current Settings**
```bash
python test_sensitivity.py "problem_file.mp3" compare
```

### **Step 3: Analyze Results**
Look at the comparison output:
- How many speech segments were detected?
- When was first speech detected?
- Does it match your manual review?

### **Step 4: Adjust Sensitivity**
- If missing faint speech → increase sensitivity (use 'high')
- If detecting too much noise → decrease sensitivity (use 'low')

### **Step 5: Validate on Batch**
Test on a larger sample of files to ensure settings work across your dataset.

---

## 🎯 Recommended Settings by Scenario

### **Scenario 1: Connection Issues (Your Current Problem)**
```python
app_settings.apply_vad_sensitivity_preset('high')
app_settings.late_hello_time = 5  # Already set
```

**Why**: Catches faint speech from poor connections while allowing extra time for network delays.

---

### **Scenario 2: High Background Noise**
```python
app_settings.apply_vad_sensitivity_preset('low')
# Keep late_hello_time at 5 for tolerance
```

**Why**: Filters out noise, only detects clear agent speech.

---

### **Scenario 3: Mixed Quality (Standard Call Center)**
```python
app_settings.apply_vad_sensitivity_preset('medium')
app_settings.late_hello_time = 5
```

**Why**: Balanced approach works for most scenarios.

---

## 🔬 Understanding the Detection Output

When you run `test_sensitivity.py`, you'll see:

```
Speech Segments Found: 5
First 10 Speech Segments:
  1. 0.125s - 0.850s (duration: 725ms)
  2. 1.200s - 2.450s (duration: 1250ms)
  ...
  
⏱️  First Speech Onset: 0.125 seconds

🏷️  CLASSIFICATION
Releasing Detection: No
Late Hello Detection: No (threshold: 5.0s)
```

### **Interpretation:**

- **Speech Segments Found**: Number of distinct speech events detected
  - 0 = Releasing (agent never spoke)
  - >0 = Agent spoke at least once

- **First Speech Onset**: Time when agent first started speaking
  - <5.0s = Normal (not late hello)
  - >5.0s = Late Hello

- **Releasing Detection**: "Yes" if no speech detected in entire call

- **Late Hello Detection**: "Yes" if first speech occurs after 5.0 seconds

---

## 🚨 Troubleshooting

### **Problem: Agent spoke but system says "Releasing"**

**Diagnosis**: Energy threshold too high, missing faint speech

**Solution**:
```python
app_settings.apply_vad_sensitivity_preset('high')
```

---

### **Problem: Background noise detected as speech**

**Diagnosis**: Energy threshold too low, picking up noise

**Solution**:
```python
app_settings.apply_vad_sensitivity_preset('low')
```

---

### **Problem: Brief "hello" not detected**

**Diagnosis**: Minimum speech duration too long

**Solution**:
```python
app_settings.vad_min_speech_duration = 80  # Reduce to 80ms
```

---

### **Problem: Network delay causing false late-hello flags**

**Diagnosis**: Late hello threshold too strict

**Solution**:
```python
app_settings.late_hello_time = 6  # Increase to 6 seconds
```

---

## 📊 Advanced: Multi-Pass Detection (Future Enhancement)

For maximum accuracy, consider implementing multi-pass detection:

1. **First Pass**: Standard sensitivity (medium)
2. **Second Pass**: If no speech found, retry with high sensitivity
3. **Validation**: Compare results, flag uncertain cases for manual review

This approach minimizes false positives while catching edge cases.

---

## 🎓 Technical Deep Dive

### **How VAD Works**

1. **Audio Preprocessing**
   - Convert to mono (left channel = agent)
   - Normalize amplitude
   - Split into 50ms frames with 25ms overlap

2. **Feature Extraction (per frame)**
   - **RMS Energy**: `sqrt(mean(signal^2))`
   - **Zero Crossing Rate**: `count(sign changes) / frame_length`

3. **Speech Classification**
   - Frame is speech if:
     - RMS Energy > threshold AND
     - 0.01 < ZCR < 0.3 (speech range)

4. **Segment Formation**
   - Merge consecutive speech frames
   - Filter segments < minimum duration
   - Return list of (start_time, end_time) tuples

### **Why These Features?**

- **RMS Energy**: Measures signal strength, distinguishes speech from silence
- **ZCR**: Distinguishes speech (complex waveform) from pure tones/hum
- **Frame-based**: Provides temporal precision for onset detection

---

## 📝 Configuration Reference

### **config.py Settings**

```python
class AppSettings:
    # Late hello detection time (seconds)
    late_hello_time = 5
    
    # VAD energy threshold (RMS units)
    vad_energy_threshold = 600
    
    # Minimum speech duration (milliseconds)
    vad_min_speech_duration = 100
    
    # Sensitivity preset
    vad_sensitivity = 'medium'  # 'high', 'medium', 'low'
```

### **Preset Values**

| Preset | Energy Threshold | Min Duration | Use Case |
|--------|------------------|--------------|----------|
| High   | 400              | 80ms         | Faint speech, poor quality |
| Medium | 600              | 100ms        | Standard recordings |
| Low    | 900              | 150ms        | High noise, clear speech only |

---

## 🎯 Summary

**Your specific problem (connection issues causing missed speech):**

✅ **Solution Implemented:**
1. Late hello window extended: 4s → 5s
2. Energy threshold lowered: 800 → 600 (default)
3. Min speech duration reduced: 150ms → 100ms
4. Configurable sensitivity presets added
5. Testing utility created

**Recommended Action:**
1. Test your problematic files with: `python test_sensitivity.py "file.mp3" compare`
2. If still missing speech, apply high sensitivity: `app_settings.apply_vad_sensitivity_preset('high')`
3. Validate on larger batch to ensure no excessive false positives

---

## 📞 Support

If you need further tuning, use the test utility to share specific examples:

```bash
python test_sensitivity.py "problem_file.mp3" compare > results.txt
```

This will help diagnose exactly what parameters work best for your audio quality.
