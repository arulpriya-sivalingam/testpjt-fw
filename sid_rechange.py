#!/usr/bin/env python3

import re
import sys
from pathlib import Path

START_SID = 40001   # starting SID number

RULE_FILE = sys.argv[1] if len(sys.argv) > 1 else None

if not RULE_FILE:
    print("Usage: python renumber_sids.py <rules-file>")
    sys.exit(1)

path = Path(RULE_FILE)
if not path.exists():
    print(f"❌ File not found: {RULE_FILE}")
    sys.exit(1)

sid_pattern = re.compile(r"sid\s*:\s*(\d+)\s*;")

current_sid = START_SID
output_lines = []

with open(RULE_FILE, "r") as f:
    for line in f:
        # Replace only if sid is found
        if "sid" in line:
            new_line = sid_pattern.sub(f"sid:{current_sid};", line)
            if new_line != line:
                current_sid += 1
        else:
            new_line = line

        output_lines.append(new_line)

# Write back to same file
with open(RULE_FILE, "w") as f:
    f.writelines(output_lines)

print(f"✅ SIDs updated starting from {START_SID}")
print(f"Updated file: {RULE_FILE}")
