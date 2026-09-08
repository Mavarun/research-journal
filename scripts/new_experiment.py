#!/usr/bin/env python3
"""Append a validated experiment to experiments/.

Example:
  python scripts/new_experiment.py \\
    --id 004_example --title "Example" \\
    --hypothesis "..." --data "..." --method "..." --result "..." \\
    --status failed --failure-reason "OOS collapsed" --retrospective
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_journal.cli import main_new  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main_new())
