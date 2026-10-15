"""Utilities for saving generated reports."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path


def save_report(markdown: str, output_dir: Path | None = None) -> Path:
    """Save a report with a timestamped filename."""
    root = output_dir or (Path(__file__).resolve().parent.parent / "reports")
    root.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("research-%Y%m%d-%H%M%S.md")
    path = root / filename
    path.write_text(markdown, encoding="utf-8")
    return path
