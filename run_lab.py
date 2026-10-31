#!/usr/bin/env python3
"""Launch the local-first AITP Laboratory browser experience."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aitp.webapp import main

if __name__ == "__main__":
    main()
