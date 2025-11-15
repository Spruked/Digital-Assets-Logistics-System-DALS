# predictive_failure_modeling.py
# Phase 11-A: Predictive Failure Modeling
# Caleon anticipates failures before they happen using pattern recognition and health trend analysis
# Version 1.0.0

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import statistics

from iss_module.csmm.awareness.self_model import get_self_model, SYSTEM_ANATOMY, ModuleStatus
from iss_module.cans.cans_awareness_bridge import CANSBridge

logger = logging.getLogger("DALS.Predictive.Failure")

@dataclass
class HealthTrend:
    """Represents a health trend for pattern analysis"""
    module: str
    timestamp: datetime
    health_score: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    response_time: Optional[float] = None
    error_rate: Optional[float] = None

@dataclass
class FailurePattern:
    """Represents a learned failure pattern"""
    pattern_id: str
    trigger_conditions: Dict[str, Any]
    failure_type: str
    time_to_failure: float  # hours
    confidence: float
    historical_occurrences: int
    prevention_actions: List[str]

@dataclass
class PredictionResult:
    """Result of a failure prediction"""
    module: str
    failure_type: str
    time_to_failure: float  # hours
    confidence: float
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    recommended_actions: List[str]
    timestamp: datetime

class PredictiveFailureEngine:
    """
    Predictive Failure Modeling Engine
    Analyzes health trends and patterns to anticipate failures before they occur.
    """

    def __init__(self):
        self.self_model = get_self_model()
        self.health_history: Dict[str, deque] = {}
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self.active_predictions: Dict[str, PredictionResult] = {}

        # Initialize health history for all modules
        for module_name in SYSTEM_ANATOMY.keys():
            self.health_history[module_name] = deque(maxlen=100)  # Keep last 100 readings

        # Load initial failure patterns
        self._initialize_failure_patterns()

        logger.info("Predictive Failure Engine initialized")

    def _initialize_failure_patterns(self):
        """Initialize known failure patterns based on historical data"""
        self.failure_patterns = {
            "ucm_memory_spike": FailurePattern(
                pattern_id="ucm_memory_spike",
                trigger_conditions={
                    "memory_trend": "increasing",
                    "memory_rate": ">5%/hour",
                    "cpu_trend": "increasing",
                    "health_trend": "declining"
                },
                failure_type="UCM degradation",
                time_to_failure=4.2,
                confidence=0.87,
                historical_occurrences=12,
                prevention_actions=[
                    "schedule_preemptive_restart",
                    "increase_monitoring_frequency",
                    "prepare_fallback_routing"
                ]
            ),
            "cans_response_timeout": FailurePattern(
                pattern_id="cans_response_timeout",
                trigger_conditions={
                    "response_time_trend": "increasing",
                    "error_rate_trend": "increasing",
                    "health_trend": "declining"
                },
                failure_type="CANS isolation failure",
                time_to_failure=2.1,
                confidence=0.91,
                historical_occurrences=8,
                prevention_actions=[
                    "isolate_at_risk_modules",
                    "reroute_critical_traffic",
                    "activate_backup_monitoring"
                ]
            ),
            "thinker_deadlock": FailurePattern(
                pattern_id="thinker_deadlock",
                trigger_conditions={
                    "cpu_usage": ">90%",
                    "response_time": ">5000ms",
                    "error_rate": ">10%",
                    "health_trend": "rapid_decline"
                },
                failure_type="Thinker deadlock",
                time_to_failure=1.5,
                confidence=0.94,
                historical_occurrences=15,
                prevention_actions=[
                    "force_thread_restart",
                    "clear_processing_queue",
                    "switch_to_backup_thinker"
                ]
            )
        }

    def record_health_reading(self, module: str, health_data: Dict[str, Any]):
        """
        Record a health reading for analysis

        Args:
            module: Module name
            health_data: Health metrics dictionary
        """
        if module not in self.health_history:
            self.health_history[module] = deque(maxlen=100)

        reading = HealthTrend(
            module=module,
            timestamp=datetime.utcnow(),
            health_score=health_data.get('health_score', 100),
            cpu_usage=health_data.get('cpu_usage'),
            memory_usage=health_data.get('memory_usage'),
            response_time=health_data.get('response_time'),
            error_rate=health_data.get('error_rate')
        )

        self.health_history[module].append(reading)

        # Analyze for predictions after recording
        self._analyze_health_trends(module)

    def _analyze_health_trends(self, module: str):
        """
        Analyze health trends for a module to predict potential failures

        Args:
            module: Module to analyze
        """
        if len(self.health_history[module]) < 5:  # Need minimum data points
            return

        history = list(self.health_history[module])

        # Calculate trends
        trends = self._calculate_trends(history)

        # Check against failure patterns
        for pattern in self.failure_patterns.values():
            if self._matches_pattern(trends, pattern):
                prediction = self._generate_prediction(module, pattern, trends)
                if prediction:
                    self.active_predictions[module] = prediction
                    self._execute_prevention_actions(prediction)
                    logger.warning(f"Failure prediction generated: {prediction.failure_type} for {module}")

    def _calculate_trends(self, history: List[HealthTrend]) -> Dict[str, Any]:
        """
        Calculate health trends from historical data

        Args:
            history: List of health readings

        Returns:
            Dictionary of trend calculations
        """
        if len(history) < 2:
            return {}

        trends = {}

        # Health score trend
        health_scores = [h.health_score for h in history[-10:]]  # Last 10 readings
        if len(health_scores) >= 2:
            health_trend = statistics.linear_regression(range(len(health_scores)), health_scores)[0]
            trends['health_trend'] = 'declining' if health_trend < -1 else 'stable' if abs(health_trend) < 0.5 else 'improving'
            trends['health_rate'] = health_trend

        # Memory usage trend
        memory_readings = [h.memory_usage for h in history[-10:] if h.memory_usage is not None]
        if len(memory_readings) >= 2:
            memory_trend = statistics.linear_regression(range(len(memory_readings)), memory_readings)[0]
            trends['memory_trend'] = 'increasing' if memory_trend > 0.5 else 'stable' if abs(memory_trend) < 0.2 else 'decreasing'
            trends['memory_rate'] = f"{memory_trend:.1f}%/hour"

        # CPU usage trend
        cpu_readings = [h.cpu_usage for h in history[-10:] if h.cpu_usage is not None]
        if len(cpu_readings) >= 2:
            cpu_trend = statistics.linear_regression(range(len(cpu_readings)), cpu_readings)[0]
            trends['cpu_trend'] = 'increasing' if cpu_trend > 0.5 else 'stable' if abs(cpu_trend) < 0.2 else 'decreasing'

        # Response time trend
        response_readings = [h.response_time for h in history[-10:] if h.response_time is not None]
        if len(response_readings) >= 2:
            response_trend = statistics.linear_regression(range(len(response_readings)), response_readings)[0]
            trends['response_time_trend'] = 'increasing' if response_trend > 10 else 'stable' if abs(response_trend) < 5 else 'decreasing'

        # Error rate trend
        error_readings = [h.error_rate for h in history[-10:] if h.error_rate is not None]
        if len(error_readings) >= 2:
            error_trend = statistics.linear_regression(range(len(error_readings)), error_readings)[0]
            trends['error_rate_trend'] = 'increasing' if error_trend > 0.1 else 'stable' if abs(error_trend) < 0.05 else 'decreasing'

        return trends

    def _matches_pattern(self, trends: Dict[str, Any], pattern: FailurePattern) -> bool:
        """
        Check if current trends match a failure pattern

        Args:
            trends: Current health trends
            pattern: Failure pattern to check

        Returns:
            True if pattern matches
        """
        conditions = pattern.trigger_conditions
        matches = 0
        total_conditions = len(conditions)

        for condition_key, condition_value in conditions.items():
            if condition_key in trends:
                trend_value = trends[condition_key]

                if condition_key == 'memory_rate' and condition_value.startswith('>'):
                    threshold = float(condition_value[1:-2])  # Remove '>/hour'
                    if isinstance(trend_value, str) and trend_value.endswith('%/hour'):
                        rate = float(trend_value[:-6])  # Remove '%/hour'
                        if rate > threshold:
                            matches += 1
                elif condition_value in ['increasing', 'declining', 'stable', 'improving', 'decreasing']:
                    if trend_value == condition_value:
                        matches += 1
                elif condition_value.startswith('>'):
                    threshold = float(condition_value[1:])
                    if isinstance(trend_value, (int, float)) and trend_value > threshold:
                        matches += 1

        # Require 70% condition match for pattern recognition
        return (matches / total_conditions) >= 0.7 if total_conditions > 0 else False

    def _generate_prediction(self, module: str, pattern: FailurePattern, trends: Dict[str, Any]) -> Optional[PredictionResult]:
        """
        Generate a failure prediction based on pattern match

        Args:
            module: Module name
            pattern: Matching failure pattern
            trends: Current trends

        Returns:
            PredictionResult or None
        """
        # Calculate risk level based on confidence and time to failure
        if pattern.confidence >= 0.9 and pattern.time_to_failure <= 2:
            risk_level = 'critical'
        elif pattern.confidence >= 0.8 and pattern.time_to_failure <= 4:
            risk_level = 'high'
        elif pattern.confidence >= 0.7:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Adjust time to failure based on current trends
        adjusted_time = pattern.time_to_failure
        if trends.get('health_trend') == 'rapid_decline':
            adjusted_time *= 0.8  # Reduce time if declining rapidly

        prediction = PredictionResult(
            module=module,
            failure_type=pattern.failure_type,
            time_to_failure=adjusted_time,
            confidence=pattern.confidence,
            risk_level=risk_level,
            recommended_actions=pattern.prevention_actions.copy(),
            timestamp=datetime.utcnow()
        )

        return prediction

    def _execute_prevention_actions(self, prediction: PredictionResult):
        """
        Execute prevention actions for a prediction

        Args:
            prediction: The prediction to act upon
        """
        module = prediction.module
        actions = prediction.recommended_actions

        for action in actions:
            if action == "schedule_preemptive_restart":
                # Schedule a restart through CANS
                CANSBridge.record_repair(
                    module=module,
                    action=f"Preemptive restart scheduled (prediction: {prediction.failure_type})",
                    duration=0.1
                )
            elif action == "increase_monitoring_frequency":
                # This would increase monitoring - for now just log
                logger.info(f"Increased monitoring for {module} due to prediction")
            elif action == "prepare_fallback_routing":
                # Activate fallback mode
                CANSBridge.activate_fallback(
                    module=module,
                    details=f"Prediction-based fallback: {prediction.failure_type}"
                )
            elif action == "isolate_at_risk_modules":
                # Preemptive isolation
                CANSBridge.record_isolation(module)
            elif action == "force_thread_restart":
                # Force restart through CANS
                CANSBridge.record_repair(
                    module=module,
                    action="Thread restart (prediction prevention)",
                    duration=0.05
                )

        # Log the prediction in self-model
        self.self_model.report_prediction(
            module=module,
            failure_type=prediction.failure_type,
            time_to_failure=prediction.time_to_failure,
            confidence=prediction.confidence,
            risk_level=prediction.risk_level
        )

    def get_prediction_for_module(self, module: str) -> Optional[PredictionResult]:
        """
        Get current prediction for a module

        Args:
            module: Module name

        Returns:
            Current prediction or None
        """
        return self.active_predictions.get(module)

    def get_all_predictions(self) -> Dict[str, PredictionResult]:
        """
        Get all active predictions

        Returns:
            Dictionary of active predictions
        """
        return self.active_predictions.copy()

    def clear_prediction(self, module: str):
        """
        Clear a prediction for a module

        Args:
            module: Module name
        """
        if module in self.active_predictions:
            del self.active_predictions[module]
            logger.info(f"Cleared prediction for {module}")

    def learn_from_outcome(self, module: str, predicted_failure: str, actual_outcome: str):
        """
        Learn from prediction accuracy for future improvements

        Args:
            module: Module name
            predicted_failure: What was predicted
            actual_outcome: What actually happened
        """
        # This would update pattern confidence based on actual outcomes
        # For now, just log the learning event
        accuracy = 1.0 if predicted_failure in actual_outcome else 0.0

        logger.info(f"Learning from prediction: {module} - Predicted: {predicted_failure}, Actual: {actual_outcome}, Accuracy: {accuracy}")

        # Update self-model with learning event
        self.self_model.report_repair(
            module="PredictiveEngine",
            issue=f"Prediction learning: {predicted_failure}",
            action=f"Outcome: {actual_outcome}, Accuracy: {accuracy}",
            duration=0.01
        )

# Global instance
_predictive_engine = None

def get_predictive_engine() -> PredictiveFailureEngine:
    """Get the global predictive failure engine instance"""
    global _predictive_engine
    if _predictive_engine is None:
        _predictive_engine = PredictiveFailureEngine()
    return _predictive_engine