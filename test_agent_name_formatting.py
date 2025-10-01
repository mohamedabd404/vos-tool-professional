"""
Test script to verify agent name formatting
Tests the conversion from 'AbdelrahmanAhmedIbrahimHassan' to 'Abdelrahman Ahmed Ibrahim Hassan'
"""

from core.audio_processor import format_agent_name_with_spaces

# Test cases
test_cases = [
    # (input, expected_output)
    ("AbdelrahmanAhmedIbrahimHassan", "Abdelrahman Ahmed Ibrahim Hassan"),
    ("JohnSmith", "John Smith"),
    ("MaryJane", "Mary Jane"),
    ("John Smith", "John Smith"),  # Already has spaces
    ("A", "A"),  # Single letter
    ("ABC", "A B C"),  # All caps
    ("JohnDoe123", "John Doe123"),  # With numbers
    ("john", "john"),  # All lowercase
    ("JOHN", "J O H N"),  # All uppercase
    ("JohnMcDonald", "John Mc Donald"),
    ("", ""),  # Empty string
]

print("=" * 70)
print("AGENT NAME FORMATTING TEST")
print("=" * 70)

all_passed = True

for input_name, expected_output in test_cases:
    result = format_agent_name_with_spaces(input_name)
    passed = result == expected_output
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}")
    print(f"  Input:    '{input_name}'")
    print(f"  Expected: '{expected_output}'")
    print(f"  Got:      '{result}'")

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 70)

# Test with real example from the issue
print("\n" + "=" * 70)
print("REAL EXAMPLE FROM ISSUE")
print("=" * 70)

filename = "AbdelrahmanAhmedIbrahimHassan_((713) 515-6252).mp3"
# Extract agent name from filename
agent_name_raw = filename.split("_")[0]
formatted_name = format_agent_name_with_spaces(agent_name_raw)

print(f"\nFilename: {filename}")
print(f"Extracted raw name: {agent_name_raw}")
print(f"Formatted name: {formatted_name}")
print(f"\nExpected: 'Abdelrahman Ahmed Ibrahim Hassan'")
print(f"Match: {'✅ YES' if formatted_name == 'Abdelrahman Ahmed Ibrahim Hassan' else '❌ NO'}")
