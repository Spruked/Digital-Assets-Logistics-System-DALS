"""
Captain's Log Engine for ISS Module
Manages journal entries, personal logs, and mission records
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from ..core.utils import get_stardate, format_timestamp
from ..core.validators import validate_log_entry, sanitize_input


@dataclass
class LogEntry:
    """Data class for log entries"""
    id: str
    timestamp: str
    stardate: float
    content: str
    tags: List[str]
    category: str
    mood: Optional[str] = None
    location: Optional[str] = None
    attachments: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class CaptainLog:
    """Captain's Log management system"""

    def __init__(self, data_dir: Optional[str] = None, captain: Optional[str] = None, ship: Optional[str] = None):
        self.data_dir = data_dir or self._get_default_data_dir()
        self.log_file = os.path.join(self.data_dir, 'captain_log.json')
        self.entries: List[LogEntry] = []
        self.logger = logging.getLogger('ISS.CaptainLog')
        self.captain = captain or "Unknown"
        self.ship = ship or "ISS Module"
        self._ensure_data_dir()

    def _get_default_data_dir(self) -> str:
        """Get default data directory"""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / 'data' / 'logs'
        return str(data_dir)

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)

    async def initialize(self):
        """Initialize the captain's log system"""
        try:
            await self.load_entries()
            self.logger.info("Captain's Log system initialized")
        except Exception as e:  # pragma: no cover - defensive
            self.logger.error(f"Failed to initialize Captain's Log: {e}")
            raise

    async def load_entries(self):
        """Load existing log entries from storage"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.entries = []
                for entry_data in data.get('entries', []):
                    entry = LogEntry(**entry_data)
                    self.entries.append(entry)

                self.logger.info(f"Loaded {len(self.entries)} log entries")
            else:
                self.entries = []
                self.logger.info("No existing log file found, starting fresh")

        except Exception as e:  # pragma: no cover - defensive
            self.logger.error(f"Failed to load log entries: {e}")
            self.entries = []

    async def save_entries(self):
        """Save log entries to storage"""
        try:
            data = {
                'version': '1.0',
                'created': format_timestamp(),
                'entries': [entry.to_dict() for entry in self.entries]
            }

            if os.path.exists(self.log_file):
                backup_file = f"{self.log_file}.backup"
                with open(self.log_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())

            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug("Log entries saved successfully")

        except Exception as e:  # pragma: no cover - defensive
            self.logger.error(f"Failed to save log entries: {e}")
            raise

    async def create_entry(
        self,
        content: str,
        category: str = 'personal',
        tags: Optional[List[str]] = None,
        mood: Optional[str] = None,
        location: Optional[str] = None
    ) -> LogEntry:
        """Create a new log entry"""
        try:
            content = sanitize_input(content, max_length=10000)
            if not content:
                raise ValueError("Log entry content cannot be empty")

            now = datetime.now(timezone.utc)
            entry = LogEntry(
                id=self._generate_entry_id(),
                timestamp=now.isoformat(),
                stardate=get_stardate(),
                content=content,
                category=category,
                tags=tags or [],
                mood=mood,
                location=location,
                attachments=[]
            )

            entry_dict = entry.to_dict()
            if not validate_log_entry(entry_dict):
                raise ValueError("Invalid log entry data")

            self.entries.append(entry)
            await self.save_entries()

            self.logger.info(f"Created log entry {entry.id}")
            return entry

        except Exception as e:  # pragma: no cover - defensive
            self.logger.error(f"Failed to create log entry: {e}")
            raise

    def add_entry_sync(
        self,
        content: str,
        category: str = 'personal',
        tags: Optional[List[str]] = None,
        mood: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """Synchronous method for adding entries"""
        try:
            entry_id = self._generate_entry_id()
            now = datetime.now(timezone.utc)
            stardate = get_stardate()

            entry_data = {
                'id': entry_id,
                'timestamp': now.isoformat(),
                'stardate': stardate,
                'content': content,
                'category': category,
                'tags': tags or [],
                'mood': mood,
                'location': location,
                'captain': self.captain,
                'ship': self.ship
            }

            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'version': '1.0', 'entries': []}

            data['entries'].append(entry_data)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Added log entry: {entry_id}")
            return entry_id

        except Exception as e:  # pragma: no cover - defensive
            self.logger.error(f"Failed to add entry: {e}")
            raise

    async def add_entry(
        self,
        content: str,
        category: str = 'personal',
        tags: Optional[List[str]] = None,
        mood: Optional[str] = None,
        location: Optional[str] = None
    ) -> LogEntry:
        """Convenient alias for create_entry"""
        return await self.create_entry(content, category, tags, mood, location)

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    async def get_entries(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[LogEntry]:
        """Retrieve log entries with optional filtering"""
        filtered_entries = self.entries.copy()

        if category:
            filtered_entries = [e for e in filtered_entries if e.category == category]

        if tags:
            filtered_entries = [
                e for e in filtered_entries
                if any(tag in e.tags for tag in tags)
            ]

        if start_date:
            filtered_entries = [
                e for e in filtered_entries
                if datetime.fromisoformat(e.timestamp.replace('Z', '+00:00')) >= start_date
            ]

        if end_date:
            filtered_entries = [
                e for e in filtered_entries
                if datetime.fromisoformat(e.timestamp.replace('Z', '+00:00')) <= end_date
            ]

        filtered_entries.sort(
            key=lambda x: datetime.fromisoformat(x.timestamp.replace('Z', '+00:00')),
            reverse=True
        )

        if limit:
            filtered_entries = filtered_entries[:limit]

        return filtered_entries

    async def get_entry_by_id(self, entry_id: str) -> Optional[LogEntry]:
        """Get a specific entry by ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    async def update_entry(
        self,
        entry_id: str,
        updates: Dict[str, Any]
    ) -> Optional[LogEntry]:
        """Update an existing entry"""
        for entry in self.entries:
            if entry.id == entry_id:
                entry_dict = entry.to_dict()
                entry_dict.update(updates)
                if not validate_log_entry(entry_dict):
                    raise ValueError("Invalid updated log entry data")
                for field, value in updates.items():
                    setattr(entry, field, value)
                await self.save_entries()
                self.logger.info(f"Updated log entry {entry_id}")
                return entry
        return None

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a log entry"""
        for entry in self.entries:
            if entry.id == entry_id:
                self.entries.remove(entry)
                await self.save_entries()
                self.logger.info(f"Deleted log entry {entry_id}")
                return True
        return False

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about log entries"""
        total_entries = len(self.entries)
        categories = {}
        moods = {}
        tags = {}

        for entry in self.entries:
            categories[entry.category] = categories.get(entry.category, 0) + 1
            if entry.mood:
                moods[entry.mood] = moods.get(entry.mood, 0) + 1
            for tag in entry.tags:
                tags[tag] = tags.get(tag, 0) + 1

        return {
            'total_entries': total_entries,
            'categories': categories,
            'moods': moods,
            'tags': tags,
        }

    async def shutdown(self):
        """Cleanup any resources (placeholder for future expansion)"""
        self.logger.info("Captain's Log shutdown complete")
