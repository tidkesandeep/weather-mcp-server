#!/usr/bin/env python3
"""Copy canonical shared/weather_broker.py into each Databricks App folder.

Databricks Apps deploy from a single folder (mcp_server/ or dashboard/), so
they cannot import across sibling packages at runtime. This script keeps both
copies identical to shared/weather_broker.py to prevent drift.

Usage:
    python scripts/sync_shared.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "shared" / "weather_broker.py"
TARGETS = [
    ROOT / "mcp_server" / "weather_broker.py",
    ROOT / "dashboard" / "weather_broker.py",
]


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing canonical broker at {SRC}", file=sys.stderr)
        return 1
    for dest in TARGETS:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC, dest)
        print(f"synced {SRC.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
