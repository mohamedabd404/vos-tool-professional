# Late Hello Detection - Issue & Fix

## Problem

Late Hello is being detected even when the agent clearly says "hello" at 2-3 seconds into the call.

**Expected Behavior:**
- Late Hello should ONLY trigger if agent's first speech is AFTER 5 seconds
- If agent speaks at 2-3 seconds → Normal (not late hello)

## Root Cause Analysis

The issue is likely caused by **Voice Activity Detection (VAD) sensitivity**:

1. **VAD detects noise as "speech"** before the actual hello
2. This noise/background sound is counted as the "first speech"
3. The actual hello at 2-3 seconds is ignored (it's the 2nd or 3rd segment)
4. If no speech is detected in first 5 seconds, it triggers Late Hello

## Current Settings

**Late Hello Threshold:** 5 seconds (correct)
**VAD Energy Threshold:** 600 (might be too sensitive)
**VAD Min Speech Duration:** 120ms

## Solution

### Option 1: Increase VAD Energy Threshold (Recommended)

This makes VAD less sensitive to background noise:

```python
# In config.py, line 106
self.vad_energy_threshold = 700  # Increase from 600 to 700 or 800
```

**Effect:** Only detects clear speech, ignores faint background noise

### Option 2: Increase Minimum Speech Duration

Require longer duration to count as speech:

```python
# In config.py, line 107
self.vad_min_speech_duration = 200  # Increase from 120ms to 200ms
```

**Effect:** Ignores very short noise bursts

### Option 3: Use Low Sensitivity Preset

```python
# In config.py, line 113
self.vad_sensitivity = 'low'  # Change from 'medium' to 'low'
```

This automatically sets:
- Energy threshold: 900
- Min speech duration: 150ms

## How to Debug

### Step 1: Test a Specific File

Run the debug script on a file that's incorrectly marked as Late Hello:

```bash
python test_late_hello_debug.py "path/to/your/audio.mp3"
```

This will show:
- Exactly when speech is detected
- All speech segments with timestamps
- Why it's classified as Late Hello

### Step 2: Check the Output

Look for this pattern (indicates the problem):

```
📊 Speech Segments:
   1.   0.50s - 0.80s  (duration: 0.30s)  ← Noise detected as speech!
   2.   2.10s - 4.50s  (duration: 2.40s)  ← Actual hello
   3.   5.20s - 6.80s  (duration: 1.60s)

⏱️ FIRST SPEECH ONSET:
   Time: 0.50 seconds  ← This is wrong! Should be 2.10s
   Threshold: 5.0 seconds
   
✅ NORMAL (On Time)  ← Correct result but for wrong reason
```

If you see early segments (< 1 second) that are just noise, increase the VAD threshold.

### Step 3: Adjust Settings

Based on the debug output:

**If you see many short segments < 0.5s:**
→ Increase `vad_min_speech_duration` to 200ms

**If you see segments starting at 0-1s (background noise):**
→ Increase `vad_energy_threshold` to 700-800

**If agent speaks clearly at 2-3s but marked as Late Hello:**
→ The VAD is detecting noise before the actual speech
→ Increase energy threshold to 800+

## Testing After Fix

1. Update the settings in `config.py`
2. Run the debug script again on the same file
3. Verify that:
   - First speech segment matches when agent actually speaks
   - No early noise segments
   - Classification is correct

## Recommended Settings for Your Use Case

Based on your description (clear hello at 2-3 seconds):

```python
# config.py
self.vad_energy_threshold = 750  # Higher = less sensitive to noise
self.vad_min_speech_duration = 150  # Ignore very short bursts
self.late_hello_time = 5  # Keep at 5 seconds
```

Or simply use:
```python
self.vad_sensitivity = 'low'  # Preset for clear speech only
```

## Quick Fix Commands

### Test a file:
```bash
python test_late_hello_debug.py "Recordings/Agent/user/agent_(123-456-7890).mp3"
```

### Temporarily change sensitivity in code:
```python
# Add this before processing in your script
from config import app_settings
app_settings.vad_energy_threshold = 800  # Less sensitive
```

## Expected Results After Fix

**Before Fix:**
```
First speech detected at: 0.50s (noise)
Late hello threshold: 5.0s
Result: NORMAL (but wrong reason)
```

**After Fix:**
```
First speech detected at: 2.30s (actual hello)
Late hello threshold: 5.0s
Result: NORMAL (correct!)
```

---

## Summary

The Late Hello threshold (5 seconds) is correct. The issue is that **VAD is too sensitive** and detects background noise as speech before the actual hello. 

**Fix:** Increase `vad_energy_threshold` from 600 to 750-800 to only detect clear speech.
