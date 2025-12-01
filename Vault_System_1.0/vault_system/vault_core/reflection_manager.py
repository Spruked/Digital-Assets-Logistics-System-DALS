# reflection_manager.py

"""
Reflection Manager - Self-Analysis and Learning System

This module manages the system's ability to reflect on its own decisions,
learn from experiences, and improve future reasoning through structured
reflection entries and pattern analysis.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class ReflectionEntry:
    """
    Represents a single reflection entry with analysis and insights.
    """

    def __init__(self, entry_type: str, trigger_event: str,
                 analysis: Dict[str, Any], insights: List[str],
                 confidence_score: float, metadata: Dict[str, Any] = None):
        """
        Initialize a reflection entry.

        Args:
            entry_type: Type of reflection (decision, error, success, etc.)
            trigger_event: What triggered this reflection
            analysis: Detailed analysis data
            insights: Key insights gained
            confidence_score: Confidence in the analysis (0.0-1.0)
            metadata: Additional metadata
        """
        self.id = f"reflection_{int(datetime.now().timestamp()*1000)}"
        self.timestamp = datetime.now()
        self.entry_type = entry_type
        self.trigger_event = trigger_event
        self.analysis = analysis
        self.insights = insights
        self.confidence_score = confidence_score
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "entry_type": self.entry_type,
            "trigger_event": self.trigger_event,
            "analysis": self.analysis,
            "insights": self.insights,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReflectionEntry':
        """Create entry from dictionary"""
        entry = cls(
            entry_type=data["entry_type"],
            trigger_event=data["trigger_event"],
            analysis=data["analysis"],
            insights=data["insights"],
            confidence_score=data["confidence_score"],
            metadata=data.get("metadata", {})
        )
        entry.id = data["id"]
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        return entry


class ReflectionVault:
    """
    Vault for storing and analyzing reflection entries.

    Provides capabilities for learning from past experiences,
    identifying patterns, and improving future decision making.
    """

    def __init__(self, storage_path: str = "./reflection_data"):
        """
        Initialize the reflection vault.

        Args:
            storage_path: Path to store reflection data
        """
        self.storage_path = storage_path
        self._ensure_storage_directory()

        # In-memory storage
        self.entries: Dict[str, ReflectionEntry] = {}

        # Pattern analysis cache
        self.pattern_cache: Dict[str, Any] = {}
        self.last_pattern_update = None

        # Load existing reflections
        self._load_reflections()

        print(f"🧠 Reflection Vault initialized at {storage_path}")

    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _load_reflections(self):
        """Load existing reflection entries from disk"""
        reflections_file = os.path.join(self.storage_path, "reflections.json")

        if os.path.exists(reflections_file):
            try:
                with open(reflections_file, 'r') as f:
                    data = json.load(f)

                for entry_data in data.get("entries", []):
                    entry = ReflectionEntry.from_dict(entry_data)
                    self.entries[entry.id] = entry

                print(f"📚 Loaded {len(self.entries)} reflection entries")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Warning: Could not load reflections: {e}")

    def _save_reflections(self):
        """Save reflection entries to disk"""
        reflections_file = os.path.join(self.storage_path, "reflections.json")

        data = {
            "entries": [entry.to_dict() for entry in self.entries.values()],
            "last_updated": datetime.now().isoformat(),
            "total_entries": len(self.entries)
        }

        with open(reflections_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_reflection(self, entry_type: str, trigger_event: str,
                      analysis: Dict[str, Any], insights: List[str],
                      confidence_score: float, metadata: Dict[str, Any] = None) -> str:
        """
        Add a new reflection entry.

        Args:
            entry_type: Type of reflection
            trigger_event: What triggered the reflection
            analysis: Analysis data
            insights: Key insights
            confidence_score: Confidence score
            metadata: Additional metadata

        Returns:
            ID of the created entry
        """
        entry = ReflectionEntry(
            entry_type=entry_type,
            trigger_event=trigger_event,
            analysis=analysis,
            insights=insights,
            confidence_score=confidence_score,
            metadata=metadata
        )

        self.entries[entry.id] = entry
        self._save_reflections()

        # Invalidate pattern cache
        self.pattern_cache = {}
        self.last_pattern_update = None

        return entry.id

    def get_reflection(self, entry_id: str) -> Optional[ReflectionEntry]:
        """Get a reflection entry by ID"""
        return self.entries.get(entry_id)

    def get_reflections_by_type(self, entry_type: str) -> List[ReflectionEntry]:
        """Get all reflections of a specific type"""
        return [
            entry for entry in self.entries.values()
            if entry.entry_type == entry_type
        ]

    def get_recent_entries(self, limit: int = 10) -> List[ReflectionEntry]:
        """Get most recent reflection entries"""
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_entries[:limit]

    def get_entries_in_timeframe(self, days: int) -> List[ReflectionEntry]:
        """Get entries from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            entry for entry in self.entries.values()
            if entry.timestamp >= cutoff
        ]

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in reflection data.

        Returns:
            Pattern analysis results
        """
        if self.pattern_cache and self.last_pattern_update:
            # Return cached results if recent
            if (datetime.now() - self.last_pattern_update).seconds < 300:  # 5 minutes
                return self.pattern_cache

        analysis = {
            "entry_type_distribution": self._analyze_entry_types(),
            "temporal_patterns": self._analyze_temporal_patterns(),
            "confidence_trends": self._analyze_confidence_trends(),
            "insight_patterns": self._analyze_insight_patterns(),
            "trigger_analysis": self._analyze_triggers(),
            "learning_progression": self._analyze_learning_progression()
        }

        # Cache results
        self.pattern_cache = analysis
        self.last_pattern_update = datetime.now()

        return analysis

    def _analyze_entry_types(self) -> Dict[str, Any]:
        """Analyze distribution of entry types"""
        type_counts = defaultdict(int)
        for entry in self.entries.values():
            type_counts[entry.entry_type] += 1

        total = len(self.entries)
        distribution = {
            entry_type: {
                "count": count,
                "percentage": round(count / total * 100, 1) if total > 0 else 0
            }
            for entry_type, count in type_counts.items()
        }

        return {
            "distribution": distribution,
            "most_common": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None,
            "total_entries": total
        }

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in reflections"""
        if not self.entries:
            return {"patterns": [], "frequency": "no_data"}

        timestamps = [entry.timestamp for entry in self.entries.values()]
        timestamps.sort()

        # Calculate time differences
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff_hours = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600
            time_diffs.append(diff_hours)

        if not time_diffs:
            return {"patterns": [], "frequency": "single_entry"}

        avg_interval = statistics.mean(time_diffs)
        std_dev = statistics.stdev(time_diffs) if len(time_diffs) > 1 else 0

        # Classify frequency
        if avg_interval < 1:
            frequency = "very_frequent"
        elif avg_interval < 6:
            frequency = "frequent"
        elif avg_interval < 24:
            frequency = "daily"
        elif avg_interval < 168:  # 7 days
            frequency = "weekly"
        else:
            frequency = "infrequent"

        return {
            "average_interval_hours": round(avg_interval, 2),
            "std_dev_hours": round(std_dev, 2),
            "frequency": frequency,
            "total_timespan_days": round((timestamps[-1] - timestamps[0]).total_seconds() / 86400, 1)
        }

    def _analyze_confidence_trends(self) -> Dict[str, Any]:
        """Analyze confidence score trends over time"""
        if not self.entries:
            return {"trend": "no_data", "average": 0, "range": [0, 0]}

        # Sort entries by time
        sorted_entries = sorted(self.entries.values(), key=lambda x: x.timestamp)
        confidence_scores = [entry.confidence_score for entry in sorted_entries]

        # Calculate trend (simple linear regression slope)
        n = len(confidence_scores)
        if n > 1:
            x = list(range(n))
            slope = statistics.linear_regression(x, confidence_scores)[0]
            trend = "increasing" if slope > 0.001 else "decreasing" if slope < -0.001 else "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "average": round(statistics.mean(confidence_scores), 3),
            "median": round(statistics.median(confidence_scores), 3),
            "range": [round(min(confidence_scores), 3), round(max(confidence_scores), 3)],
            "std_dev": round(statistics.stdev(confidence_scores), 3) if n > 1 else 0
        }

    def _analyze_insight_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in insights"""
        all_insights = []
        for entry in self.entries.values():
            all_insights.extend(entry.insights)

        if not all_insights:
            return {"patterns": [], "total_insights": 0}

        # Count insight frequencies
        insight_counts = defaultdict(int)
        for insight in all_insights:
            insight_counts[insight] += 1

        # Find common themes
        common_insights = sorted(
            insight_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_insights": len(all_insights),
            "unique_insights": len(insight_counts),
            "most_common_insights": common_insights,
            "avg_insights_per_entry": round(len(all_insights) / len(self.entries), 2) if self.entries else 0
        }

    def _analyze_triggers(self) -> Dict[str, Any]:
        """Analyze what triggers reflections"""
        trigger_counts = defaultdict(int)
        for entry in self.entries.values():
            trigger_counts[entry.trigger_event] += 1

        sorted_triggers = sorted(
            trigger_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "trigger_distribution": dict(sorted_triggers),
            "most_common_trigger": sorted_triggers[0][0] if sorted_triggers else None,
            "unique_triggers": len(trigger_counts)
        }

    def _analyze_learning_progression(self) -> Dict[str, Any]:
        """Analyze learning progression over time"""
        if len(self.entries) < 2:
            return {"progression": "insufficient_data"}

        # Sort by time
        sorted_entries = sorted(self.entries.values(), key=lambda x: x.timestamp)

        # Track confidence progression
        confidence_progression = [entry.confidence_score for entry in sorted_entries]

        # Simple progression analysis
        first_half = confidence_progression[:len(confidence_progression)//2]
        second_half = confidence_progression[len(confidence_progression)//2:]

        if first_half and second_half:
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            improvement = second_avg - first_avg

            if improvement > 0.1:
                progression = "significant_improvement"
            elif improvement > 0.05:
                progression = "moderate_improvement"
            elif improvement > -0.05:
                progression = "stable"
            else:
                progression = "declining"
        else:
            progression = "insufficient_data"

        return {
            "progression": progression,
            "confidence_improvement": round(improvement, 3) if 'improvement' in locals() else 0,
            "total_entries_analyzed": len(sorted_entries)
        }

    def get_learning_recommendations(self) -> List[str]:
        """
        Generate learning recommendations based on reflection analysis.

        Returns:
            List of recommendation strings
        """
        if not self.entries:
            return ["Collect more reflection data to generate recommendations"]

        patterns = self.analyze_patterns()
        recommendations = []

        # Confidence-based recommendations
        confidence_analysis = patterns.get("confidence_trends", {})
        if confidence_analysis.get("trend") == "decreasing":
            recommendations.append("Confidence is declining - review recent decision processes")
        elif confidence_analysis.get("trend") == "stable":
            recommendations.append("Consider introducing new learning challenges to improve confidence")

        # Frequency recommendations
        temporal = patterns.get("temporal_patterns", {})
        if temporal.get("frequency") == "infrequent":
            recommendations.append("Increase reflection frequency for better learning")
        elif temporal.get("frequency") == "very_frequent":
            recommendations.append("Reduce reflection frequency to focus on quality over quantity")

        # Trigger diversity
        trigger_analysis = patterns.get("trigger_analysis", {})
        if trigger_analysis.get("unique_triggers", 0) < 3:
            recommendations.append("Diversify reflection triggers to gain broader insights")

        # Insight quality
        insight_patterns = patterns.get("insight_patterns", {})
        if insight_patterns.get("avg_insights_per_entry", 0) < 1:
            recommendations.append("Focus on generating more insights per reflection")

        return recommendations if recommendations else ["Continue current reflection practices"]

    def export_reflections(self, filepath: str, format_type: str = "json") -> bool:
        """
        Export reflection data to file.

        Args:
            filepath: Export file path
            format_type: Export format (json, csv)

        Returns:
            Success status
        """
        try:
            if format_type == "json":
                data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "total_entries": len(self.entries),
                    "entries": [entry.to_dict() for entry in self.entries.values()]
                }
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

            elif format_type == "csv":
                import csv
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "id", "timestamp", "type", "trigger", "confidence",
                        "insights_count", "analysis_keys"
                    ])

                    for entry in self.entries.values():
                        writer.writerow([
                            entry.id,
                            entry.timestamp.isoformat(),
                            entry.entry_type,
                            entry.trigger_event,
                            entry.confidence_score,
                            len(entry.insights),
                            ",".join(entry.analysis.keys())
                        ])

            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def get_total_entries(self) -> int:
        """Get total number of reflection entries"""
        return len(self.entries)

    def clear_old_entries(self, days_to_keep: int = 365) -> int:
        """
        Clear reflection entries older than specified days.

        Args:
            days_to_keep: Number of days of entries to keep

        Returns:
            Number of entries removed
        """
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        old_entries = [
            entry_id for entry_id, entry in self.entries.items()
            if entry.timestamp < cutoff
        ]

        for entry_id in old_entries:
            del self.entries[entry_id]

        if old_entries:
            self._save_reflections()

        return len(old_entries)