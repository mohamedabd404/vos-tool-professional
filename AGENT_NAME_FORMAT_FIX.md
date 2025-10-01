# Agent Name Formatting Fix

## Problem

Agent names from the dialer were not formatted properly in the recordings table. Names appeared without spaces, causing display and matching issues.

### Example:
- **Filename**: `AbdelrahmanAhmedIbrahimHassan_((713) 515-6252).mp3`
- **Displayed as**: `AbdelrahmanAhmedIbrahimHassan` ❌
- **Should be**: `Abdelrahman Ahmed Ibrahim Hassan` ✅

## Root Cause

The issue occurred in two places:

### 1. During Download (`automation/download_readymode_calls.py`)
**Lines 315 & 414** - Agent names were extracted with `.replace(" ", "")`:
```python
agent_text = block.find_element(...).text.strip().replace(" ", "")
```
This removed ALL spaces from agent names when creating filenames.

### 2. During Analysis (`core/audio_processor.py`)
**Line 154** - Agent names were cleaned again:
```python
agent_name = agent_name.replace(" ", "").replace("-", "").replace(".", "")
```
This removed spaces when extracting names from filenames for display.

## Solution

### Two-Part Fix:

#### Part 1: Preserve Original Names During Download
**Modified**: `automation/download_readymode_calls.py`

1. **Keep spaces in agent names** when extracting from dialer (lines 324, 424):
   ```python
   # OLD: agent_text = ...text.strip().replace(" ", "")
   # NEW: agent_text = ...text.strip()  # Keep spaces!
   ```

2. **Remove spaces only for filenames** using new helper function:
   ```python
   def format_agent_name_for_filename(agent_name):
       """Remove spaces for filesystem compatibility"""
       return agent_name.strip().replace(" ", "")
   ```

3. **Use formatted name for filename only** (lines 344, 444):
   ```python
   filename = f"{format_agent_name_for_filename(agent_name)}_({phone_number}).mp3"
   ```

**Result**: 
- Agent name in memory: `"Abdelrahman Ahmed Ibrahim Hassan"` (with spaces)
- Filename on disk: `"AbdelrahmanAhmedIbrahimHassan_(713-515-6252).mp3"` (no spaces)

#### Part 2: Restore Spaces During Analysis
**Modified**: `core/audio_processor.py`

1. **Added helper function** to restore spaces (lines 16-37):
   ```python
   def format_agent_name_with_spaces(agent_name: str) -> str:
       """
       Convert 'AbdelrahmanAhmedIbrahimHassan' 
       to 'Abdelrahman Ahmed Ibrahim Hassan'
       """
       if ' ' in agent_name:
           return agent_name  # Already has spaces
       
       # Add space before each capital letter
       return re.sub(r'(?<!^)(?=[A-Z])', ' ', agent_name)
   ```

2. **Updated name extraction** (lines 168-182):
   ```python
   # Extract from filename
   agent_name_raw = filename.split("_")[0]
   
   # Clean special characters
   agent_name_raw = agent_name_raw.replace("-", "").replace(".", "")
   
   # Format with proper spacing
   agent_name = format_agent_name_with_spaces(agent_name_raw)
   ```

**Result**: Filenames like `AbdelrahmanAhmedIbrahimHassan` are displayed as `Abdelrahman Ahmed Ibrahim Hassan`

## How It Works

### The Regex Pattern
```python
re.sub(r'(?<!^)(?=[A-Z])', ' ', agent_name)
```

**Breakdown**:
- `(?<!^)` - Negative lookbehind: NOT at the start of string
- `(?=[A-Z])` - Positive lookahead: followed by a capital letter
- Insert a space at these positions

**Examples**:
- `JohnSmith` → `John Smith`
- `AbdelrahmanAhmed` → `Abdelrahman Ahmed`
- `ABC` → `A B C`
- `John Smith` → `John Smith` (already has spaces, returned as-is)

## Testing

Run the test script to verify:
```bash
python test_agent_name_formatting.py
```

**Test Results**:
```
✅ ALL TESTS PASSED!

Real Example:
Filename: AbdelrahmanAhmedIbrahimHassan_((713) 515-6252).mp3
Formatted: Abdelrahman Ahmed Ibrahim Hassan ✅
```

## Files Modified

1. **`automation/download_readymode_calls.py`**
   - Added `format_agent_name_for_filename()` helper function
   - Removed `.replace(" ", "")` from agent extraction (2 places)
   - Use helper function when creating filenames (2 places)

2. **`core/audio_processor.py`**
   - Added `format_agent_name_with_spaces()` helper function
   - Updated agent name extraction to preserve and restore spacing
   - Import `re` module for regex

3. **`test_agent_name_formatting.py`** (New)
   - Comprehensive test suite for name formatting
   - Tests edge cases and real examples

## Benefits

✅ **Consistent Display**: Names match dialer format with proper spacing  
✅ **Filesystem Safe**: Filenames still use no-space format  
✅ **Backward Compatible**: Works with existing files without spaces  
✅ **Forward Compatible**: Works with new files that have spaces  
✅ **Better UX**: Names are readable in tables and reports

## Edge Cases Handled

- **Already has spaces**: Returns as-is
- **All caps**: `ABC` → `A B C`
- **Mixed case**: `JohnSmith` → `John Smith`
- **With numbers**: `John123` → `John123`
- **Empty string**: Returns empty
- **Single letter**: `A` → `A`

## Migration Notes

### For Existing Files
Old files without spaces in filenames will automatically be formatted with spaces when displayed:
- File: `JohnSmith_(123-456-7890).mp3`
- Display: `John Smith`

### For New Downloads
New downloads will:
1. Extract agent name WITH spaces from dialer
2. Save filename WITHOUT spaces (for compatibility)
3. Display WITH spaces in tables

No manual migration needed! 🎉
