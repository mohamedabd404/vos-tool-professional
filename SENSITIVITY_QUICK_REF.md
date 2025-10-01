# VAD Sensitivity Quick Reference Card

## 🎯 Current Settings (After Update)

| Parameter | Old Value | New Value | Impact |
|-----------|-----------|-----------|--------|
| Late Hello Threshold | 4.0s | **5.0s** | More tolerance for network delays |
| Energy Threshold | 800 | **600** | Detects fainter speech |
| Min Speech Duration | 150ms | **100ms** | Catches brief utterances |

---

## 🎚️ Sensitivity Presets

### Quick Apply
```python
from config import app_settings

# For connection issues / faint speech
app_settings.apply_vad_sensitivity_preset('high')

# For standard quality
app_settings.apply_vad_sensitivity_preset('medium')

# For noisy environments
app_settings.apply_vad_sensitivity_preset('low')
```

### Preset Comparison

| Preset | Energy | Duration | Best For |
|--------|--------|----------|----------|
| **HIGH** | 400 | 80ms | Faint speech, poor connections |
| **MEDIUM** | 600 | 100ms | Standard recordings (default) |
| **LOW** | 900 | 150ms | High noise, clear speech only |

---

## 🧪 Testing Commands

### Test single file
```bash
python test_sensitivity.py "path/to/audio.mp3" medium
```

### Compare all presets
```bash
python test_sensitivity.py "path/to/audio.mp3" compare
```

---

## 🔧 Manual Override

### In config.py
```python
# In AppSettings.__init__()
self.vad_energy_threshold = 500      # Custom value
self.vad_min_speech_duration = 90    # Custom value (ms)
self.late_hello_time = 5             # Seconds
```

### At runtime
```python
from config import app_settings

app_settings.vad_energy_threshold = 550
app_settings.vad_min_speech_duration = 95
app_settings.late_hello_time = 6
```

---

## 🚨 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent spoke but flagged as "Releasing" | Use `'high'` sensitivity |
| Background noise detected as speech | Use `'low'` sensitivity |
| Brief "hello" not detected | Reduce `vad_min_speech_duration` to 80ms |
| Network delay causing late-hello flags | Increase `late_hello_time` to 6s |

---

## 📊 What Gets Measured

### Energy Threshold
- **Measures**: Audio signal strength (RMS)
- **Lower = more sensitive** (detects quieter sounds)
- **Higher = less sensitive** (only loud sounds)

### Min Speech Duration
- **Measures**: Minimum length of valid speech
- **Lower = more sensitive** (catches brief sounds)
- **Higher = less sensitive** (filters short noises)

### Late Hello Time
- **Measures**: Maximum acceptable delay before agent speaks
- **Lower = stricter** (flags more calls)
- **Higher = more tolerant** (allows longer delays)

---

## 🎯 Recommended for Your Use Case

**Problem**: Connection issues causing faint/unclear speech to be missed

**Solution**:
```python
from config import app_settings

# Apply high sensitivity for connection issues
app_settings.apply_vad_sensitivity_preset('high')

# Late hello already set to 5s (good for network delays)
print(f"Late hello threshold: {app_settings.late_hello_time}s")
```

**Test on problematic files**:
```bash
python test_sensitivity.py "problem_call.mp3" compare
```

---

## 📈 Optimization Process

1. **Collect** problematic audio files
2. **Test** with: `python test_sensitivity.py "file.mp3" compare`
3. **Analyze** which preset works best
4. **Apply** that preset in config.py
5. **Validate** on larger batch

---

## 💡 Pro Tips

- Start with `'high'` sensitivity for connection issue scenarios
- Use `compare` mode to see all three presets side-by-side
- If you get too many false positives, dial back to `'medium'`
- Keep `late_hello_time` at 5s for network tolerance
- Test on 10-20 files before deploying to production

---

## 📞 Need More Help?

See full documentation: `VAD_SENSITIVITY_GUIDE.md`
