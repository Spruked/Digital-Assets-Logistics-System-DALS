"""
VisiData integration helpers for captain mode tooling.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional

from .captain_log import LogEntry
from .exporters import Exporters
from ..core.utils import ensure_folder

logger = logging.getLogger("ISS.CaptainMode.VisiData")


class VisiDataWrapper:
    """Minimal bridge between captain logs and VisiData."""

    def __init__(self, export_folder: str = "vd_exports") -> None:
        self.export_folder = ensure_folder(export_folder)

    def _export(self, entries: Iterable[LogEntry], filename: str, fmt: str) -> Optional[Path]:
        path = Path(self.export_folder) / filename
        if fmt == "csv":
            Exporters.to_csv(entries, str(path))
        elif fmt == "json":
            Exporters.to_json(entries, str(path))
        elif fmt == "md":
            Exporters.to_markdown(entries, str(path))
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return path

    def export_to_csv(self, entries: Iterable[LogEntry], filename: str = "vd_export.csv") -> Optional[Path]:
        return self._export(entries, filename, "csv")

    def export_to_json(self, entries: Iterable[LogEntry], filename: str = "vd_export.json") -> Optional[Path]:
        return self._export(entries, filename, "json")

    def open_in_visidata(self, file_path: Path) -> bool:
        try:
            subprocess.run(["vd", str(file_path)], check=False)
            return True
        except FileNotFoundError:
            logger.error("VisiData not installed or not in PATH")
            return False
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to launch VisiData: %s", exc)
            return False

    async def view_log_entries(self, entries: List[LogEntry], format_type: str = "csv", launch_immediately: bool = True) -> str:
        filename = "vd_log_entries.csv" if format_type == "csv" else "vd_log_entries.json"
        path = self._export(entries, filename, format_type if format_type in {"csv", "json", "md"} else "csv")
        if path and launch_immediately:
            self.open_in_visidata(path)
        return str(path) if path else ""

    def cleanup(self) -> None:
        try:
            path = Path(self.export_folder)
            if path.exists():
                for child in path.glob("*"):
                    child.unlink()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to cleanup VisiData export folder: %s", exc)
