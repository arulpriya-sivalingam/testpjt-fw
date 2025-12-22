#!/usr/bin/env python3
import re
from pathlib import Path

RULESTRING_RE = re.compile(r"^\s*RuleString\s*:\s*>\-?\s*$")
CAPACITY_RE = re.compile(r"^\s*Capacity\s*:\s*.*$", re.IGNORECASE)

def extract_rule_blocks(text: str) -> list[str]:
    """
    Extract ALL Suricata rule blocks in a YAML file:
      start: line exactly like 'RuleString: >-' (or 'RuleString:>-')
      end:   line starting with 'Capacity:'
    Returns list of extracted blocks (dedented).
    """
    lines = text.splitlines()
    blocks: list[str] = []

    in_block = False
    block_indent = None
    captured: list[str] = []

    for line in lines:
        if not in_block:
            if RULESTRING_RE.match(line):
                in_block = True
                block_indent = None
                captured = []
            continue

        # End of current block
        if CAPACITY_RE.match(line):
            rules_text = "\n".join(captured).rstrip() + "\n"
            blocks.append(rules_text)
            in_block = False
            block_indent = None
            captured = []
            continue

        # Preserve blank lines
        if line.strip() == "":
            captured.append("")
            continue

        # Determine indentation level of the block content from the first non-empty line
        if block_indent is None:
            block_indent = len(line) - len(line.lstrip(" "))

        # Dedent safely
        cur_indent = len(line) - len(line.lstrip(" "))
        if cur_indent >= (block_indent or 0):
            captured.append(line[(block_indent or 0):])
        else:
            captured.append(line.lstrip(" "))

    return blocks

def main() -> int:
    base = Path("networkfirewall/rule-groups")
    if not base.exists():
        print(f"ERROR: Folder not found: {base}")
        return 1

    out_dir = Path("reports/extracted_rules")
    out_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = list(base.rglob("*.yml")) + list(base.rglob("*.yaml"))
    if not yaml_files:
        print(f"ERROR: No .yml/.yaml files found under {base}")
        return 1

    total_blocks = 0
    for yf in sorted(yaml_files):
        text = yf.read_text(encoding="utf-8", errors="replace")
        if "RuleString" not in text:
            continue

        blocks = extract_rule_blocks(text)
        if not blocks:
            continue

        # Write each block to a separate .rules file
        for idx, rules_text in enumerate(blocks, start=1):
            suffix = f"-{idx}" if len(blocks) > 1 else ""
            out_name = f"{yf.stem}{suffix}.rules"
            out_path = out_dir / out_name
            out_path.write_text(rules_text, encoding="utf-8")
            print(f"[extract] {yf} -> {out_path}")
            total_blocks += 1

    if total_blocks == 0:
        print("ERROR: No RuleString blocks found in any rule-group YAML files.")
        return 1

    print(f"Extracted total RuleString blocks: {total_blocks}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
