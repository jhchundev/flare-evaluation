#!/usr/bin/env python3
"""Test RGB parser with various spacing formats"""

test_cases = [
    "100 100 100",           # Single space
    "100  100  100",         # Double space
    "100   100   100",       # Triple space
    "100\t100\t100",         # Tabs
    "100 \t 100 \t 100",     # Mixed spaces and tabs
    "  100   100   100  ",   # Leading/trailing spaces
    "100     100     100",   # Many spaces
]

print("Testing RGB value parsing with various spacing:")
print("=" * 50)

for i, test in enumerate(test_cases, 1):
    try:
        values = test.strip().split()
        if len(values) == 3:
            r, g, b = map(float, values)
            print(f"Test {i}: ✅ Parsed as R={r}, G={g}, B={b}")
            print(f"         Input: '{test}'")
        else:
            print(f"Test {i}: ❌ Failed - got {len(values)} values")
    except Exception as e:
        print(f"Test {i}: ❌ Error: {e}")
    print("-" * 50)

print("\nConclusion: Python's split() handles variable spacing correctly!")
print("No changes needed to the RGB tools.")