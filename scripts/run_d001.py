#!/usr/bin/env python3
"""Repository entry point for the Checkpoint 1 D001 smoke run."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skillnudge.d001 import main


if __name__ == "__main__":
    raise SystemExit(main())
