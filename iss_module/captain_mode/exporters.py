"""
Data export helpers for captain mode.
These utilities mirror the legacy ISS captain_mode exporters that the
voice pipeline expects, while staying lightweight for DALS.
"""

from __future__ import annotations

import csv
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .captain_log import CaptainLog, LogEntry

logger = logging.getLogger("ISS.CaptainMode.Exporters")


class Exporters:
    """Static helpers for writing structured data to disk."""

    @staticmethod
    def _prepare_rows(data: Iterable[Any]) -> List[Dict[str, Any]]:
        if data is None:
            return []
        rows: List[Dict[str, Any]] = []
        for item in data:
            if isinstance(item, LogEntry):
                rows.append(asdict(item))
            elif isinstance(item, dict):
                rows.append(dict(item))
            else:
                logger.debug("Skipping unsupported export row type: %s", type(item))
        return rows

    @staticmethod
    def _ensure_parent(path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def to_json(cls, data: Iterable[Any], filepath: str, *, indent: int = 2) -> bool:
        rows = cls._prepare_rows(data)
        cls._ensure_parent(filepath)
        payload = {
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "records": rows,
        }
        with open(filepath, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=indent, ensure_ascii=False)
        return True

    @classmethod
    def to_csv(cls, data: Iterable[Any], filepath: str) -> bool:
        rows = cls._prepare_rows(data)
        cls._ensure_parent(filepath)
        fieldnames: List[str]
        if rows:
            fieldnames = sorted({key for row in rows for key in row.keys()})
        else:
            fieldnames = []
        with open(filepath, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return True

    @classmethod
    def to_markdown(cls, data: Iterable[Any], filepath: str) -> bool:
        rows = cls._prepare_rows(data)
        cls._ensure_parent(filepath)
        lines: List[str] = []
        lines.append("# Captain Log Export")
        lines.append("")
        lines.append(f"Exported: {datetime.utcnow().isoformat()}Z")
        lines.append("")
        if not rows:
            lines.append("*(no entries)*")
        else:
            headers = sorted({key for row in rows for key in row.keys()})
            header_row = " | ".join(headers)
            separator = " | ".join(["---"] * len(headers))
            lines.append(f"| {header_row} |")
            lines.append(f"| {separator} |")
            for row in rows:
                ordered = [str(row.get(col, "")) for col in headers]
                lines.append(f"| {' | '.join(ordered)} |")
        with open(filepath, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
        return True

    # Convenience aliases for compatibility with older code paths
    @classmethod
    def to_json_sync(cls, data: Iterable[Any], filepath: str) -> str:
        cls.to_json(data, filepath)
        return filepath

    @classmethod
    def to_csv_sync(cls, data: Iterable[Any], filepath: str) -> str:
        cls.to_csv(data, filepath)
        return filepath

    @classmethod
    def to_markdown_sync(cls, data: Iterable[Any], filepath: str) -> str:
        cls.to_markdown(data, filepath)
        return filepath


class DataExporter:
    """Async-friendly wrapper that mirrors the legacy interface."""

    def __init__(self, output_dir: Optional[str] = None):
        base = Path(output_dir) if output_dir else Path(__file__).parent.parent / "data" / "exports"
        self.output_dir = base
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("ISS.CaptainMode.DataExporter")

    def _build_path(self, stem: str, extension: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{stem}_{timestamp}.{extension}"
        return str(self.output_dir / filename)

    async def export_log_entries_json(self, entries: List[LogEntry], filename: Optional[str] = None) -> str:
        path = filename or self._build_path("captain_log_export", "json")
        Exporters.to_json(entries, path)
        self.logger.info("Exported %s log entries to %s", len(entries), path)
        return path

    async def export_log_entries_csv(self, entries: List[LogEntry], filename: Optional[str] = None) -> str:
        path = filename or self._build_path("captain_log_export", "csv")
        Exporters.to_csv(entries, path)
        self.logger.info("Exported %s log entries to %s", len(entries), path)
        return path

    async def export_log_entries_markdown(self, entries: List[LogEntry], filename: Optional[str] = None) -> str:
        path = filename or self._build_path("captain_log_export", "md")
        Exporters.to_markdown(entries, path)
        self.logger.info("Exported %s log entries to %s", len(entries), path)
        return path

    async def export_statistics_json(self, captain_log: CaptainLog, filename: Optional[str] = None) -> str:
        stats = await captain_log.get_statistics()
        path = filename or self._build_path("captain_log_statistics", "json")
        payload = {
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "statistics": stats,
        }
        Exporters.to_json([payload], path)
        self.logger.info("Exported captain log statistics to %s", path)
        return path

    async def create_backup(self, captain_log: CaptainLog, filename: Optional[str] = None) -> str:
        entries = await captain_log.get_entries()
        path = filename or self._build_path("captain_log_backup", "json")
        Exporters.to_json(entries, path)
        self.logger.info("Created captain log backup at %s", path)
        return path

    # Compatibility helpers -------------------------------------------------
    @staticmethod
    def to_csv_sync(data: Iterable[Any], filepath: str) -> str:
        return Exporters.to_csv_sync(data, filepath)

    @staticmethod
    def to_json_sync(data: Iterable[Any], filepath: str) -> str:
        return Exporters.to_json_sync(data, filepath)

    @staticmethod
    def to_markdown_sync(data: Iterable[Any], filepath: str) -> str:
        return Exporters.to_markdown_sync(data, filepath)
