"""
Learning Engine

Analyzes repair patterns and improves diagnostic capabilities.
Learns from successful and failed repairs to enhance system reliability.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

from iss_module.core.utils import get_stardate, current_timecodes
from iss_module.core.caleon_security_layer import CaleonSecurityLayer
from iss_module.csmm.models.csmm_models import (
    RepairAction,
    ComponentIssue,
    LearningPattern,
    DiagnosticRule
)

logger = logging.getLogger("DALS.CSMM.Learning")

class LearningEngine:
    """
    CSMM Learning Engine

    Analyzes repair patterns to:
    - Identify recurring issues
    - Improve diagnostic accuracy
    - Predict potential failures
    - Optimize repair strategies
    - Generate proactive maintenance recommendations
    """

    def __init__(self):
        self.security_layer = CaleonSecurityLayer()
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.diagnostic_rules: Dict[str, DiagnosticRule] = {}
        self.component_failure_patterns: Dict[str, List[ComponentIssue]] = defaultdict(list)
        self.repair_success_rates: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.predictive_insights: List[Dict[str, Any]] = []

        # Learning thresholds
        self.min_samples_for_pattern = 3
        self.confidence_threshold = 0.7
        self.pattern_retention_days = 30

    async def analyze_repair_outcome(self, repair: RepairAction) -> None:
        """
        Analyze a completed repair action to extract learning insights

        Args:
            repair: The completed repair action
        """
        try:
            logger.info("Analyzing repair outcome", extra={
                "correlation_id": repair.id,
                "target_component": repair.target_component,
                "action_type": repair.action_type,
                "status": repair.status.value,
                "stardate": get_stardate()
            })

            # Validate security permissions
            security_check = await self.security_layer.validate_reasoning_request(
                query=f"CSMM learning analysis: {repair.id}",
                mode="sequential",
                ethical_check=True
            )

            if not security_check.get("approved", False):
                logger.warning("Learning analysis blocked by Caleon security", extra={
                    "correlation_id": repair.id,
                    "reason": security_check.get("reasoning", "unknown")
                })
                return

            # Extract learning insights
            await self._extract_failure_patterns(repair)
            await self._update_success_rates(repair)
            await self._generate_predictive_insights(repair)
            await self._update_diagnostic_rules(repair)

            # Clean up old patterns
            await self._cleanup_old_patterns()

        except Exception as e:
            logger.error(f"Failed to analyze repair outcome: {e}", extra={
                "correlation_id": repair.id,
                "error": str(e)
            })

    async def _extract_failure_patterns(self, repair: RepairAction) -> None:
        """Extract failure patterns from repair data"""
        component = repair.target_component
        action_type = repair.action_type

        # Store failure pattern
        if repair.status == "failed":
            failure_pattern = {
                "component": component,
                "action_type": action_type,
                "error_message": repair.error_message,
                "timestamp": repair.completed_at,
                "stardate": get_stardate(),
                "frequency": 1
            }

            pattern_key = f"{component}_{action_type}"
            if pattern_key in self.learning_patterns:
                self.learning_patterns[pattern_key].frequency += 1
                self.learning_patterns[pattern_key].last_occurrence = repair.completed_at
            else:
                self.learning_patterns[pattern_key] = LearningPattern(
                    pattern_id=pattern_key,
                    component=component,
                    action_type=action_type,
                    frequency=1,
                    success_rate=0.0,
                    first_occurrence=repair.completed_at,
                    last_occurrence=repair.completed_at,
                    common_errors=[repair.error_message] if repair.error_message else []
                )

    async def _update_success_rates(self, repair: RepairAction) -> None:
        """Update success rates for repair actions"""
        component = repair.target_component
        action_type = repair.action_type

        key = f"{component}_{action_type}"
        if key not in self.repair_success_rates:
            self.repair_success_rates[key]["total"] = 0
            self.repair_success_rates[key]["successful"] = 0

        self.repair_success_rates[key]["total"] += 1
        if repair.status == "completed":
            self.repair_success_rates[key]["successful"] += 1

        # Calculate success rate
        total = self.repair_success_rates[key]["total"]
        successful = self.repair_success_rates[key]["successful"]
        success_rate = successful / total if total > 0 else 0.0

        # Update learning pattern
        if key in self.learning_patterns:
            self.learning_patterns[key].success_rate = success_rate

    async def _generate_predictive_insights(self, repair: RepairAction) -> None:
        """Generate predictive insights from repair patterns"""
        component = repair.target_component

        # Check for recurring failures
        recent_failures = [
            p for p in self.learning_patterns.values()
            if p.component == component and p.frequency >= self.min_samples_for_pattern
        ]

        for pattern in recent_failures:
            if pattern.success_rate < self.confidence_threshold:
                insight = {
                    "type": "predictive_maintenance",
                    "component": component,
                    "pattern": pattern.pattern_id,
                    "risk_level": "high" if pattern.success_rate < 0.5 else "medium",
                    "recommendation": f"Consider proactive maintenance for {component}",
                    "confidence": pattern.success_rate,
                    "generated_at": current_timecodes()["iso_timestamp"],
                    "stardate": get_stardate()
                }

                self.predictive_insights.append(insight)

                # Keep only recent insights
                if len(self.predictive_insights) > 50:
                    self.predictive_insights = self.predictive_insights[-50:]

                logger.info("Generated predictive insight", extra={
                    "component": component,
                    "pattern": pattern.pattern_id,
                    "risk_level": insight["risk_level"],
                    "stardate": get_stardate()
                })

    async def _update_diagnostic_rules(self, repair: RepairAction) -> None:
        """Update diagnostic rules based on repair outcomes"""
        component = repair.target_component
        action_type = repair.action_type

        # Create or update diagnostic rule
        rule_key = f"rule_{component}_{action_type}"

        if rule_key not in self.diagnostic_rules:
            self.diagnostic_rules[rule_key] = DiagnosticRule(
                rule_id=rule_key,
                component=component,
                condition=f"Component {component} requires {action_type}",
                action=action_type,
                confidence=0.5,
                created_at=current_timecodes()["iso_timestamp"],
                last_updated=current_timecodes()["iso_timestamp"]
            )

        rule = self.diagnostic_rules[rule_key]

        # Update confidence based on success rate
        pattern_key = f"{component}_{action_type}"
        if pattern_key in self.learning_patterns:
            pattern = self.learning_patterns[pattern_key]
            rule.confidence = pattern.success_rate
            rule.last_updated = current_timecodes()["iso_timestamp"]

            # Add common error patterns
            if repair.error_message and repair.error_message not in rule.common_errors:
                rule.common_errors.append(repair.error_message)
                if len(rule.common_errors) > 5:  # Keep only 5 most recent
                    rule.common_errors = rule.common_errors[-5:]

    async def _cleanup_old_patterns(self) -> None:
        """Clean up old learning patterns"""
        cutoff_date = datetime.now() - timedelta(days=self.pattern_retention_days)
        cutoff_iso = cutoff_date.isoformat()

        # Remove old patterns
        patterns_to_remove = []
        for pattern_id, pattern in self.learning_patterns.items():
            if pattern.last_occurrence < cutoff_iso:
                patterns_to_remove.append(pattern_id)

        for pattern_id in patterns_to_remove:
            del self.learning_patterns[pattern_id]

        # Remove old insights
        self.predictive_insights = [
            insight for insight in self.predictive_insights
            if insight["generated_at"] > cutoff_iso
        ]

        if patterns_to_remove:
            logger.info(f"Cleaned up {len(patterns_to_remove)} old learning patterns", extra={
                "stardate": get_stardate()
            })

    async def get_learning_insights(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get learning insights for a component or all components

        Args:
            component: Specific component to get insights for, or None for all

        Returns:
            Dict with learning insights
        """
        if component:
            patterns = {
                k: v for k, v in self.learning_patterns.items()
                if v.component == component
            }
            insights = [
                insight for insight in self.predictive_insights
                if insight["component"] == component
            ]
        else:
            patterns = self.learning_patterns
            insights = self.predictive_insights

        return {
            "patterns": {
                k: {
                    "component": v.component,
                    "action_type": v.action_type,
                    "frequency": v.frequency,
                    "success_rate": v.success_rate,
                    "last_occurrence": v.last_occurrence
                }
                for k, v in patterns.items()
            },
            "predictive_insights": insights,
            "diagnostic_rules": {
                k: {
                    "component": v.component,
                    "condition": v.condition,
                    "action": v.action,
                    "confidence": v.confidence,
                    "last_updated": v.last_updated
                }
                for k, v in self.diagnostic_rules.items()
                if component is None or v.component == component
            },
            "generated_at": current_timecodes()["iso_timestamp"],
            "stardate": get_stardate()
        }

    async def get_component_health_score(self, component: str) -> Dict[str, Any]:
        """
        Calculate health score for a component based on learning data

        Args:
            component: Component to score

        Returns:
            Dict with health score and factors
        """
        patterns = [
            p for p in self.learning_patterns.values()
            if p.component == component
        ]

        if not patterns:
            return {
                "component": component,
                "health_score": 1.0,  # Perfect health if no patterns
                "risk_level": "low",
                "factors": ["No repair history"],
                "calculated_at": current_timecodes()["iso_timestamp"]
            }

        # Calculate weighted health score
        total_weight = 0
        weighted_score = 0

        for pattern in patterns:
            weight = pattern.frequency
            score = pattern.success_rate
            total_weight += weight
            weighted_score += (score * weight)

        health_score = weighted_score / total_weight if total_weight > 0 else 1.0

        # Determine risk level
        if health_score >= 0.8:
            risk_level = "low"
        elif health_score >= 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"

        factors = []
        for pattern in patterns:
            if pattern.success_rate < 0.7:
                factors.append(f"Low success rate for {pattern.action_type} ({pattern.success_rate:.2f})")
            if pattern.frequency >= self.min_samples_for_pattern:
                factors.append(f"Recurring issues with {pattern.action_type} ({pattern.frequency} times)")

        return {
            "component": component,
            "health_score": round(health_score, 3),
            "risk_level": risk_level,
            "factors": factors if factors else ["Good repair history"],
            "calculated_at": current_timecodes()["iso_timestamp"],
            "stardate": get_stardate()
        }

    async def predict_component_failures(self, component: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Predict potential failures for a component

        Args:
            component: Component to predict for
            days_ahead: Number of days to look ahead

        Returns:
            List of predicted failure scenarios
        """
        patterns = [
            p for p in self.learning_patterns.values()
            if p.component == component and p.frequency >= self.min_samples_for_pattern
        ]

        predictions = []

        for pattern in patterns:
            if pattern.success_rate < self.confidence_threshold:
                # Calculate failure probability based on pattern
                failure_probability = 1.0 - pattern.success_rate

                prediction = {
                    "component": component,
                    "predicted_issue": pattern.action_type,
                    "probability": round(failure_probability, 3),
                    "timeframe_days": days_ahead,
                    "confidence": pattern.success_rate,
                    "based_on_samples": pattern.frequency,
                    "recommended_action": f"Monitor {component} closely",
                    "predicted_at": current_timecodes()["iso_timestamp"],
                    "stardate": get_stardate()
                }

                predictions.append(prediction)

        return sorted(predictions, key=lambda x: x["probability"], reverse=True)

    async def export_learning_data(self) -> Dict[str, Any]:
        """
        Export all learning data for backup or analysis

        Returns:
            Dict with all learning data
        """
        return {
            "learning_patterns": {
                k: v.dict() for k, v in self.learning_patterns.items()
            },
            "diagnostic_rules": {
                k: v.dict() for k, v in self.diagnostic_rules.items()
            },
            "repair_success_rates": dict(self.repair_success_rates),
            "predictive_insights": self.predictive_insights,
            "exported_at": current_timecodes()["iso_timestamp"],
            "stardate": get_stardate()
        }

    async def import_learning_data(self, data: Dict[str, Any]) -> bool:
        """
        Import learning data from backup

        Args:
            data: Learning data to import

        Returns:
            bool: True if import successful
        """
        try:
            # Validate data structure
            required_keys = ["learning_patterns", "diagnostic_rules", "repair_success_rates", "predictive_insights"]
            if not all(key in data for key in required_keys):
                logger.error("Invalid learning data structure")
                return False

            # Import patterns
            for k, v in data["learning_patterns"].items():
                self.learning_patterns[k] = LearningPattern(**v)

            # Import rules
            for k, v in data["diagnostic_rules"].items():
                self.diagnostic_rules[k] = DiagnosticRule(**v)

            # Import success rates
            self.repair_success_rates.update(data["repair_success_rates"])

            # Import insights
            self.predictive_insights = data["predictive_insights"]

            logger.info("Learning data imported successfully", extra={
                "patterns_count": len(self.learning_patterns),
                "rules_count": len(self.diagnostic_rules),
                "stardate": get_stardate()
            })

            return True

        except Exception as e:
            logger.error(f"Failed to import learning data: {e}")
            return False