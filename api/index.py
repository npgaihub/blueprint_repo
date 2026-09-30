"""Vercel entrypoint. vercel.json rewrites every path to this function."""

import sys
from pathlib import Path

# Make the src/ layout importable regardless of how Vercel installs the project.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app.main import app

__all__ = ["app"]
