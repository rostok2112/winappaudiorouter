"""Backward-compatible wrapper for the refactored package."""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from winappaudiorouter import *  # noqa: F401,F403
from winappaudiorouter.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
