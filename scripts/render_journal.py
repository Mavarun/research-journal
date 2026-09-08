#!/usr/bin/env python3
"""Render a markdown summary table from experiments/.

Example:
  python scripts/render_journal.py
  python scripts/render_journal.py -o JOURNAL.md
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_journal.cli import main_render  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main_render())
