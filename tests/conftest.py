from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    # Allow running `python -m pytest` without installing the package.
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"
    sys.path.insert(0, str(src_dir))
