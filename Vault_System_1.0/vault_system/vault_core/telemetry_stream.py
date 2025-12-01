# telemetry_stream.py

"""
Telemetry Stream - Real-time System Monitoring and Analytics

This module provides comprehensive telemetry capabilities for monitoring
system health, performance metrics, and operational status in real-time.
"""

import time
import threading
import json
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics


class TelemetryLevel(Enum):
    """Telemetry reporting levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics that can be tracked"""
    COUNTER = "counter"       # Monotonically increasing value
    GAUGE = "gauge"          # Value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Duration measurements


class TelemetryEvent:
    """
    Represents a single telemetry event with timestamp and metadata.
    """

    def __init__(self, event_type: str, component: str, action: str,
                 duration: float = None, success: Optional[bool] = None,
                 metadata: Dict[str, Any] = None):
        """
        Initialize a telemetry event.

        Args:
            event_type: Type of event (system, user, error, etc.)
            component: Component that generated the event
            action: Action that was performed
            duration: Duration in seconds (optional)
            success: Whether the action was successful (optional)
            metadata: Additional metadata
        """
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.component = component
        self.action = action
        self.duration = duration
        self.success = success
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "component": self.component,
            "action": self.action,
            "duration": self.duration,
            "success": self.success,
            "metadata": self.metadata
        }


class Metric:
    """
    Represents a single metric with value and metadata.
    """

    def __init__(self, name: str, metric_type: MetricType, value: Any,
                 tags: Dict[str, str] = None):
        """
        Initialize a metric.

        Args:
            name: Metric name
            metric_type: Type of metric
            value: Metric value
            tags: Dimension tags
        """
        self.name = name
        self.metric_type = metric_type
        self.value = value
        self.tags = tags or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat()
        }


class TelemetryManager:
    """
    Central telemetry manager for collecting, storing, and analyzing
    system metrics and events.
    """

    def __init__(self, storage_path: str = "./telemetry_data",
                 max_events: int = 10000, max_metrics: int = 5000):
        """
        Initialize the telemetry manager.

        Args:
            storage_path: Path to store telemetry data
            max_events: Maximum number of events to keep in memory
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.storage_path = storage_path
        self._ensure_storage_directory()

        # Event storage (circular buffers)
        self.events: deque[TelemetryEvent] = deque(maxlen=max_events)
        self.metrics: deque[Metric] = deque(maxlen=max_metrics)

        # Real-time metrics
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)

        # Alert system
        self.alerts: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable] = []

        # Background processing
        self.running = False
        self.processing_thread = None
        self.save_interval = 60  # Save every 60 seconds

        # Load existing data
        self._load_telemetry_data()

        print(f"📊 Telemetry Manager initialized at {storage_path}")

    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _load_telemetry_data(self):
        """Load existing telemetry data from disk"""
        events_file = os.path.join(self.storage_path, "events.json")
        metrics_file = os.path.join(self.storage_path, "metrics.json")

        # Load events
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r') as f:
                    data = json.load(f)
                    for event_data in data.get("events", []):
                        # Convert back to TelemetryEvent
                        event = TelemetryEvent(
                            event_type=event_data["event_type"],
                            component=event_data["component"],
                            action=event_data["action"],
                            duration=event_data.get("duration"),
                            success=event_data.get("success"),
                            metadata=event_data.get("metadata", {})
                        )
                        event.timestamp = datetime.fromisoformat(event_data["timestamp"])
                        self.events.append(event)
            except Exception as e:
                print(f"⚠️  Warning: Could not load events: {e}")

        # Load metrics
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    for metric_data in data.get("metrics", []):
                        metric = Metric(
                            name=metric_data["name"],
                            metric_type=MetricType(metric_data["type"]),
                            value=metric_data["value"],
                            tags=metric_data.get("tags", {})
                        )
                        metric.timestamp = datetime.fromisoformat(metric_data["timestamp"])
                        self.metrics.append(metric)
            except Exception as e:
                print(f"⚠️  Warning: Could not load metrics: {e}")

    def _save_telemetry_data(self):
        """Save telemetry data to disk"""
        events_file = os.path.join(self.storage_path, "events.json")
        metrics_file = os.path.join(self.storage_path, "metrics.json")

        # Save events
        events_data = {
            "events": [event.to_dict() for event in self.events],
            "last_updated": datetime.now().isoformat()
        }
        with open(events_file, 'w') as f:
            json.dump(events_data, f, indent=2)

        # Save metrics
        metrics_data = {
            "metrics": [metric.to_dict() for metric in self.metrics],
            "last_updated": datetime.now().isoformat()
        }
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)

    def record_event(self, event_type: str, component: str, action: str,
                    duration: float = None, success: bool = None,
                    metadata: Dict[str, Any] = None):
        """
        Record a telemetry event.

        Args:
            event_type: Type of event
            component: Component name
            action: Action performed
            duration: Duration in seconds
            success: Success status
            metadata: Additional metadata
        """
        event = TelemetryEvent(
            event_type=event_type,
            component=component,
            action=action,
            duration=duration,
            success=success,
            metadata=metadata
        )

        self.events.append(event)

        # Check for alerts
        self._check_alerts(event)

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """
        Increment a counter metric.

        Args:
            name: Counter name
            value: Value to increment by
            tags: Dimension tags
        """
        self.counters[name] += value

        metric = Metric(name, MetricType.COUNTER, self.counters[name], tags)
        self.metrics.append(metric)

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Set a gauge metric value.

        Args:
            name: Gauge name
            value: Value to set
            tags: Dimension tags
        """
        self.gauges[name] = value

        metric = Metric(name, MetricType.GAUGE, value, tags)
        self.metrics.append(metric)

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Record a value in a histogram.

        Args:
            name: Histogram name
            value: Value to record
            tags: Dimension tags
        """
        self.histograms[name].append(value)

        # Keep only last 1000 values
        if len(self.histograms[name]) > 1000:
            self.histograms[name] = self.histograms[name][-1000:]

        metric = Metric(name, MetricType.HISTOGRAM, value, tags)
        self.metrics.append(metric)

    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """
        Record a timer duration.

        Args:
            name: Timer name
            duration: Duration in seconds
            tags: Dimension tags
        """
        self.timers[name].append(duration)

        # Keep only last 1000 values
        if len(self.timers[name]) > 1000:
            self.timers[name] = self.timers[name][-1000:]

        metric = Metric(name, MetricType.TIMER, duration, tags)
        self.metrics.append(metric)

    def time_function(self, name: str, tags: Dict[str, str] = None):
        """
        Decorator to time function execution.

        Args:
            name: Timer name
            tags: Dimension tags

        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.record_timer(name, duration, tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.record_timer(f"{name}_error", duration, tags)
                    raise e
            return wrapper
        return decorator

    def add_alert_rule(self, name: str, condition: Callable[[TelemetryEvent], bool],
                      level: TelemetryLevel, message: str):
        """
        Add an alert rule.

        Args:
            name: Alert rule name
            condition: Function that returns True if alert should trigger
            level: Alert severity level
            message: Alert message
        """
        alert_rule = {
            "name": name,
            "condition": condition,
            "level": level,
            "message": message,
            "active": True
        }
        self.alerts.append(alert_rule)

    def _check_alerts(self, event: TelemetryEvent):
        """Check if any alerts should be triggered"""
        for alert in self.alerts:
            if alert["active"] and alert["condition"](event):
                self._trigger_alert(alert, event)

    def _trigger_alert(self, alert: Dict[str, Any], event: TelemetryEvent):
        """Trigger an alert"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "rule_name": alert["name"],
            "level": alert["level"].value,
            "message": alert["message"],
            "trigger_event": event.to_dict()
        }

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                print(f"⚠️  Alert callback failed: {e}")

        # Record alert as event
        self.record_event(
            "alert",
            "telemetry_manager",
            "alert_triggered",
            metadata={"alert_data": alert_data}
        )

    def add_alert_callback(self, callback: Callable):
        """
        Add a callback function for alerts.

        Args:
            callback: Function to call when alert is triggered
        """
        self.alert_callbacks.append(callback)

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health metrics.

        Returns:
            Health metrics dictionary
        """
        # Calculate health scores
        recent_events = list(self.events)[-100:]  # Last 100 events

        if not recent_events:
            return {"overall_health": "unknown", "metrics": {}}

        # Error rate
        error_events = [e for e in recent_events if e.event_type == "error"]
        error_rate = len(error_events) / len(recent_events)

        # Success rate
        success_events = [e for e in recent_events if e.success is True]
        success_rate = len(success_events) / len(recent_events) if recent_events else 0

        # Performance metrics
        duration_events = [e for e in recent_events if e.duration is not None]
        avg_duration = statistics.mean([e.duration for e in duration_events]) if duration_events else 0

        # Overall health score (0-100)
        health_score = (success_rate * 100) - (error_rate * 50)
        health_score = max(0, min(100, health_score))

        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 75:
            health_status = "good"
        elif health_score >= 60:
            health_status = "fair"
        elif health_score >= 40:
            health_status = "poor"
        else:
            health_status = "critical"

        return {
            "overall_health": health_status,
            "health_score": round(health_score, 1),
            "metrics": {
                "error_rate": round(error_rate, 3),
                "success_rate": round(success_rate, 3),
                "avg_response_time": round(avg_duration, 3),
                "total_events": len(self.events),
                "total_metrics": len(self.metrics)
            },
            "recent_activity": {
                "events_last_hour": len([e for e in recent_events
                                       if (datetime.now() - e.timestamp).seconds < 3600]),
                "errors_last_hour": len([e for e in recent_events
                                       if e.event_type == "error" and
                                       (datetime.now() - e.timestamp).seconds < 3600])
            }
        }

    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """
        Get statistics for a specific component.

        Args:
            component: Component name

        Returns:
            Component statistics
        """
        component_events = [e for e in self.events if e.component == component]

        if not component_events:
            return {"component": component, "stats": "no_data"}

        # Event type distribution
        event_types = defaultdict(int)
        for event in component_events:
            event_types[event.event_type] += 1

        # Success rate
        success_count = sum(1 for e in component_events if e.success is True)
        total_with_success = sum(1 for e in component_events if e.success is not None)
        success_rate = success_count / total_with_success if total_with_success > 0 else 0

        # Average duration
        durations = [e.duration for e in component_events if e.duration is not None]
        avg_duration = statistics.mean(durations) if durations else 0

        return {
            "component": component,
            "total_events": len(component_events),
            "event_types": dict(event_types),
            "success_rate": round(success_rate, 3),
            "avg_duration": round(avg_duration, 3),
            "time_range": {
                "oldest": min(e.timestamp for e in component_events).isoformat(),
                "newest": max(e.timestamp for e in component_events).isoformat()
            }
        }

    def get_metric_summary(self, metric_name: str, metric_type: MetricType = None) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.

        Args:
            metric_name: Name of the metric
            metric_type: Type of metric (optional)

        Returns:
            Metric summary
        """
        relevant_metrics = [
            m for m in self.metrics
            if m.name == metric_name and (metric_type is None or m.metric_type == metric_type)
        ]

        if not relevant_metrics:
            return {"metric": metric_name, "summary": "no_data"}

        values = [m.value for m in relevant_metrics]

        if metric_type == MetricType.COUNTER:
            return {
                "metric": metric_name,
                "type": "counter",
                "current_value": values[-1] if values else 0,
                "total_increments": len(values)
            }

        elif metric_type == MetricType.GAUGE:
            return {
                "metric": metric_name,
                "type": "gauge",
                "current_value": values[-1] if values else 0,
                "min": min(values),
                "max": max(values),
                "avg": round(statistics.mean(values), 3)
            }

        elif metric_type == MetricType.HISTOGRAM:
            return {
                "metric": metric_name,
                "type": "histogram",
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": round(statistics.mean(values), 3),
                "median": round(statistics.median(values), 3),
                "p95": round(statistics.quantiles(values, n=20)[18], 3) if len(values) >= 20 else None
            }

        elif metric_type == MetricType.TIMER:
            return {
                "metric": metric_name,
                "type": "timer",
                "count": len(values),
                "avg_duration": round(statistics.mean(values), 3),
                "min_duration": min(values),
                "max_duration": max(values),
                "p95_duration": round(statistics.quantiles(values, n=20)[18], 3) if len(values) >= 20 else None
            }

        return {"metric": metric_name, "summary": "unknown_type"}

    def export_telemetry(self, filepath: str, format_type: str = "json",
                        time_range: Optional[tuple] = None) -> bool:
        """
        Export telemetry data.

        Args:
            filepath: Export file path
            format_type: Export format
            time_range: Optional (start, end) datetime tuple

        Returns:
            Success status
        """
        try:
            # Filter by time range if specified
            if time_range:
                start_time, end_time = time_range
                filtered_events = [e for e in self.events if start_time <= e.timestamp <= end_time]
                filtered_metrics = [m for m in self.metrics if start_time <= m.timestamp <= end_time]
            else:
                filtered_events = list(self.events)
                filtered_metrics = list(self.metrics)

            if format_type == "json":
                data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "events": [event.to_dict() for event in filtered_events],
                    "metrics": [metric.to_dict() for metric in filtered_metrics],
                    "summary": self.get_system_health()
                }
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def start_background_processing(self):
        """Start background processing thread"""
        if self.running:
            return

        self.running = True
        self.processing_thread = threading.Thread(target=self._background_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def stop_background_processing(self):
        """Stop background processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)

    def _background_worker(self):
        """Background worker for periodic tasks"""
        last_save = time.time()

        while self.running:
            current_time = time.time()

            # Periodic save
            if current_time - last_save >= self.save_interval:
                self._save_telemetry_data()
                last_save = current_time

            time.sleep(1)  # Check every second

    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old telemetry data.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Number of items removed
        """
        cutoff = datetime.now() - timedelta(days=days_to_keep)

        # Remove old events
        old_events = [e for e in self.events if e.timestamp < cutoff]
        for event in old_events:
            self.events.remove(event)

        # Remove old metrics
        old_metrics = [m for m in self.metrics if m.timestamp < cutoff]
        for metric in old_metrics:
            self.metrics.remove(metric)

        removed_count = len(old_events) + len(old_metrics)

        if removed_count > 0:
            self._save_telemetry_data()

        return removed_count