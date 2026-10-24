"""Runtime settings, read from the environment."""

from __future__ import annotations

import os
from pathlib import Path

MODEL = os.environ.get("MVA_MODEL", "claude-opus-5-5")
CACHE_DIR = Path(os.environ.get("MVA_CACHE_DIR", ".cache"))
ALLOW_VARIANT_LOOKUP = os.environ.get("MVA_ALLOW_VARIANT_LOOKUP", "0") == "1"
MAX_TURNS = int(os.environ.get("MVA_MAX_TURNS", "10"))
FALLBACK = os.environ.get("MVA_FALLBACK", "1") == "1"
