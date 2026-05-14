#!/usr/bin/env python3
"""Validate the structure of a Perfect It report."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "# Perfect It Report",
    "## Confidence",
    "## Candidate Strategy",
    "## Evidence",
    "## Remaining Blockers",
    "## Final Strategy",
    "## Confidence Gate",
]

GATE_ITEMS = [
    "Success criteria are explicit and testable.",
    "Material loopholes are fixed, impossible, accepted, or proven irrelevant.",
    "Critical assumptions are backed by evidence.",
    "Verification ran successfully, or skipped checks are immaterial.",
    "Final strategy is not more fragile than the original.",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-report.py path/to/report.md", file=sys.stderr)
        return 2

    report_path = Path(sys.argv[1]).expanduser()
    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        return 2

    text = report_path.read_text(encoding="utf-8")
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"Missing heading: {heading}")

    if not re.search(r"Status:\s*(100% CONFIDENT|NOT 100% CONFIDENT)", text):
        errors.append("Missing confidence status: 'Status: 100% CONFIDENT' or 'Status: NOT 100% CONFIDENT'")

    if not re.search(r"Final status:\s*(100% CONFIDENT|NOT 100% CONFIDENT)", text):
        errors.append("Missing final status: 'Final status: 100% CONFIDENT' or 'Final status: NOT 100% CONFIDENT'")

    for item in GATE_ITEMS:
        if item not in text:
            errors.append(f"Missing confidence gate item: {item}")

    if "Final status: 100% CONFIDENT" in text:
        unchecked = re.findall(r"- \[ \] .+", text)
        if unchecked:
            errors.append("Final status is 100% CONFIDENT but at least one confidence gate item is unchecked")

        blockers_match = re.search(
            r"## Remaining Blockers\s*(.*?)\s*## Final Strategy",
            text,
            flags=re.DOTALL,
        )
        blockers = blockers_match.group(1).strip() if blockers_match else ""
        if blockers and blockers not in {"- None", "None"}:
            errors.append("Final status is 100% CONFIDENT but remaining blockers are not empty")

    if errors:
        print("Perfect It report validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Perfect It report validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
