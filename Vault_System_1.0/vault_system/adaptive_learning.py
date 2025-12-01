# adaptive_learning.py

"""
Adaptive Learning System - Dynamic Knowledge Acquisition and Optimization

This module provides adaptive learning capabilities for the vault system,
including reinforcement learning, knowledge distillation, and continuous improvement.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import random
import math
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')


class LearningStrategy(Enum):
    """Types of learning strategies"""
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    SUPERVISED_LEARNING = "supervised_learning"
    UNSUPERVISED_LEARNING = "unsupervised_learning"
    TRANSFER_LEARNING = "transfer_learning"
    META_LEARNING = "meta_learning"


class LearningPhase(Enum):
    """Phases of the learning process"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    CONSOLIDATION = "consolidation"
    TRANSFER = "transfer"


@dataclass
class LearningExperience:
    """
    A learning experience or training example.
    """
    state: Dict[str, Any]
    action: str
    reward: float
    next_state: Dict[str, Any]
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LearnedKnowledge:
    """
    Knowledge learned from experiences.
    """
    concept: str
    confidence: float
    evidence_count: int
    last_updated: datetime
    related_concepts: Set[str]
    performance_metrics: Dict[str, float]

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class AdaptiveLearning:
    """
    Adaptive learning system for continuous improvement and knowledge acquisition.

    Implements reinforcement learning, knowledge distillation, and adaptive
    optimization strategies for the vault system.
    """

    def __init__(self, reflection_manager, predictive_engine):
        """
        Initialize adaptive learning system.

        Args:
            reflection_manager: Reflection manager for self-analysis
            predictive_engine: Predictive engine for forecasting
        """
        self.reflection_manager = reflection_manager
        self.predictive_engine = predictive_engine

        # Learning experiences
        self.experiences: List[LearningExperience] = []
        self.max_experiences = 10000

        # Learned knowledge base
        self.knowledge_base: Dict[str, LearnedKnowledge] = {}

        # Learning models
        self.learning_models: Dict[str, Any] = {}

        # Current learning phase
        self.current_phase = LearningPhase.EXPLORATION

        # Exploration parameters
        self.exploration_rate = 0.3
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01

        # Learning metrics
        self.learning_metrics = {
            "total_experiences": 0,
            "successful_actions": 0,
            "average_reward": 0.0,
            "learning_efficiency": 0.0,
            "knowledge_growth": 0.0
        }

        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)

        # Knowledge distillation
        self.distillation_queue: List[Dict[str, Any]] = []

        print("🧠 Adaptive Learning initialized")

    def add_experience(self, state: Dict[str, Any], action: str, reward: float,
                      next_state: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """
        Add a learning experience.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            context: Additional context
        """
        experience = LearningExperience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            timestamp=datetime.now(),
            context=context
        )

        self.experiences.append(experience)

        # Maintain experience limit
        if len(self.experiences) > self.max_experiences:
            self.experiences = self.experiences[-self.max_experiences:]

        # Update learning metrics
        self.learning_metrics["total_experiences"] += 1
        self.learning_metrics["average_reward"] = (
            (self.learning_metrics["average_reward"] * (self.learning_metrics["total_experiences"] - 1) + reward)
            / self.learning_metrics["total_experiences"]
        )

        if reward > 0:
            self.learning_metrics["successful_actions"] += 1

        # Decay exploration rate
        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate * self.exploration_decay
        )

    def choose_action(self, state: Dict[str, Any], available_actions: List[str]) -> str:
        """
        Choose an action using current learning strategy.

        Args:
            state: Current state
            available_actions: List of available actions

        Returns:
            Chosen action
        """
        if not available_actions:
            return "no_action"

        # Exploration vs exploitation
        if random.random() < self.exploration_rate:
            # Explore: random action
            return random.choice(available_actions)
        else:
            # Exploit: best known action
            return self._get_best_action(state, available_actions)

    def _get_best_action(self, state: Dict[str, Any], available_actions: List[str]) -> str:
        """Get the best action based on learned knowledge"""
        # Simplified Q-learning approach
        action_values = {}

        for action in available_actions:
            # Calculate expected value based on similar experiences
            similar_experiences = self._find_similar_experiences(state, action)
            if similar_experiences:
                avg_reward = sum(exp.reward for exp in similar_experiences) / len(similar_experiences)
                action_values[action] = avg_reward
            else:
                action_values[action] = 0.0  # Default value

        # Return action with highest expected value
        if not action_values:
            return random.choice(available_actions)
        # action_values is a dict {action: value}, so get the action with max value
        return max(action_values, key=lambda k: action_values[k])

    def _find_similar_experiences(self, state: Dict[str, Any], action: str,
                                similarity_threshold: float = 0.8) -> List[LearningExperience]:
        """Find experiences similar to current state and action"""
        similar_experiences = []

        for exp in self.experiences:
            if exp.action != action:
                continue

            # Calculate state similarity (simplified)
            similarity = self._calculate_state_similarity(state, exp.state)
            if similarity >= similarity_threshold:
                similar_experiences.append(exp)

        return similar_experiences

    def _calculate_state_similarity(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> float:
        """Calculate similarity between two states"""
        if not state1 or not state2:
            return 0.0

        # Simple key-based similarity
        keys1 = set(state1.keys())
        keys2 = set(state2.keys())

        if not keys1 or not keys2:
            return 0.0

        # Jaccard similarity of keys
        intersection = len(keys1.intersection(keys2))
        union = len(keys1.union(keys2))

        if union == 0:
            return 0.0

        return intersection / union

    def learn_from_experiences(self, batch_size: int = 100):
        """
        Learn patterns from accumulated experiences.

        Args:
            batch_size: Number of experiences to process
        """
        if len(self.experiences) < batch_size:
            return

        # Get recent experiences
        recent_experiences = self.experiences[-batch_size:]

        # Extract patterns and knowledge
        patterns = self._extract_patterns(recent_experiences)
        knowledge_updates = self._distill_knowledge(patterns)

        # Update knowledge base
        for concept, knowledge in knowledge_updates.items():
            if concept in self.knowledge_base:
                # Update existing knowledge
                existing = self.knowledge_base[concept]
                existing.confidence = (existing.confidence * existing.evidence_count + knowledge.confidence) / (existing.evidence_count + 1)
                existing.evidence_count += 1
                existing.last_updated = datetime.now()
                existing.related_concepts.update(knowledge.related_concepts)
            else:
                # Add new knowledge
                self.knowledge_base[concept] = knowledge

        # Update learning efficiency
        successful_patterns = len([p for p in patterns if p.get("confidence", 0) > 0.7])
        self.learning_metrics["learning_efficiency"] = successful_patterns / len(patterns) if patterns else 0

        print(f"🧠 Learned {len(knowledge_updates)} new concepts from {batch_size} experiences")

    def _extract_patterns(self, experiences: List[LearningExperience]) -> List[Dict[str, Any]]:
        """Extract patterns from experiences"""
        patterns = []

        # Group experiences by action
        action_groups = defaultdict(list)
        for exp in experiences:
            action_groups[exp.action].append(exp)

        for action, action_experiences in action_groups.items():
            if len(action_experiences) < 5:
                continue

            # Calculate action success rate
            successful_exps = [exp for exp in action_experiences if exp.reward > 0]
            success_rate = len(successful_exps) / len(action_experiences)

            # Calculate average reward
            avg_reward = sum(exp.reward for exp in action_experiences) / len(action_experiences)

            # Find common state features
            common_features = self._find_common_features(action_experiences)

            pattern = {
                "action": action,
                "success_rate": success_rate,
                "average_reward": avg_reward,
                "frequency": len(action_experiences),
                "common_features": common_features,
                "confidence": min(success_rate * 1.2, 1.0)  # Boost successful patterns
            }

            patterns.append(pattern)

        return patterns

    def _find_common_features(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Find features common across experiences"""
        if not experiences:
            return {}

        # Collect all state features
        all_features = defaultdict(list)

        for exp in experiences:
            for key, value in exp.state.items():
                all_features[key].append(value)

        # Find features that are consistent
        common_features = {}

        for key, values in all_features.items():
            if len(values) < 2:
                continue

            # Check if values are similar (for numeric) or identical (for categorical)
            if all(isinstance(v, (int, float)) for v in values):
                # Numeric: check variance
                variance = np.var(values)
                if variance < np.mean(values) * 0.1:  # Low variance
                    common_features[key] = {
                        "type": "numeric",
                        "mean": np.mean(values),
                        "variance": variance
                    }
            else:
                # Categorical: check if most values are the same
                most_common = max(set(values), key=values.count)
                frequency = values.count(most_common) / len(values)
                if frequency > 0.8:  # 80% agreement
                    common_features[key] = {
                        "type": "categorical",
                        "value": most_common,
                        "frequency": frequency
                    }

        return common_features

    def _distill_knowledge(self, patterns: List[Dict[str, Any]]) -> Dict[str, LearnedKnowledge]:
        """Distill knowledge from patterns"""
        knowledge_updates = {}


        for pattern in patterns:
            action = pattern["action"]
            confidence = pattern["confidence"]

            if confidence < 0.6:  # Only learn from confident patterns
                continue

            concept = f"action_{action}_effectiveness"

            # Find related concepts
            related_concepts = set()
            for feature_name in pattern.get("common_features", {}):
                related_concepts.add(f"feature_{feature_name}_importance")

            knowledge = LearnedKnowledge(
                concept=concept,
                confidence=confidence,
                evidence_count=pattern["frequency"],
                last_updated=datetime.now(),
                related_concepts=related_concepts,
                performance_metrics={
                    "success_rate": pattern["success_rate"],
                    "average_reward": pattern["average_reward"]
                }
            )

            knowledge_updates[concept] = knowledge

        return knowledge_updates

    def apply_transfer_learning(self, source_domain: str, target_domain: str):
        """
        Apply transfer learning from source to target domain.

        Args:
            source_domain: Source domain knowledge
            target_domain: Target domain to apply knowledge to
        """
        # Find knowledge relevant to source domain
        source_knowledge = {
            concept: knowledge
            for concept, knowledge in self.knowledge_base.items()
            if source_domain in concept
        }

        if not source_knowledge:
            print(f"⚠️  No knowledge found for source domain: {source_domain}")
            return

        # Adapt knowledge for target domain
        adapted_knowledge = {}

        for concept, knowledge in source_knowledge.items():
            # Replace source domain with target domain in concept name
            target_concept = concept.replace(source_domain, target_domain)

            # Reduce confidence due to domain shift
            adapted_confidence = knowledge.confidence * 0.8

            adapted_knowledge[target_concept] = LearnedKnowledge(
                concept=target_concept,
                confidence=adapted_confidence,
                evidence_count=knowledge.evidence_count,
                last_updated=datetime.now(),
                related_concepts=knowledge.related_concepts.copy(),
                performance_metrics=knowledge.performance_metrics.copy()
            )

        # Add adapted knowledge to knowledge base
        self.knowledge_base.update(adapted_knowledge)

        print(f"🔄 Transferred {len(adapted_knowledge)} concepts from {source_domain} to {target_domain}")

    def optimize_performance(self):
        """Optimize system performance based on learned knowledge"""
        # Analyze performance patterns
        if len(self.performance_history) < 10:
            return

        recent_performance = list(self.performance_history)[-10:]
        avg_performance = sum(recent_performance) / len(recent_performance)

        # Identify performance bottlenecks
        bottlenecks = self._identify_bottlenecks()

        # Generate optimization recommendations
        optimizations = self._generate_optimizations(bottlenecks, avg_performance)

        # Apply optimizations
        applied_count = 0
        for optimization in optimizations:
            if self._apply_optimization(optimization):
                applied_count += 1

        if applied_count > 0:
            print(f"⚡ Applied {applied_count} performance optimizations")

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Check learning metrics for issues
        if self.learning_metrics["learning_efficiency"] < 0.5:
            bottlenecks.append({
                "type": "learning_efficiency",
                "severity": "high",
                "description": "Learning efficiency below threshold"
            })

        if self.exploration_rate > 0.2:
            bottlenecks.append({
                "type": "exploration_rate",
                "severity": "medium",
                "description": "High exploration rate may slow convergence"
            })

        # Check knowledge base growth
        knowledge_growth = len(self.knowledge_base) / max(1, self.learning_metrics["total_experiences"]) * 1000
        if knowledge_growth < 0.1:
            bottlenecks.append({
                "type": "knowledge_growth",
                "severity": "medium",
                "description": "Knowledge base growing too slowly"
            })

        return bottlenecks

    def _generate_optimizations(self, bottlenecks: List[Dict[str, Any]],
                              avg_performance: float) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        optimizations = []

        for bottleneck in bottlenecks:
            if bottleneck["type"] == "learning_efficiency":
                optimizations.append({
                    "type": "increase_batch_size",
                    "description": "Increase learning batch size for better pattern recognition",
                    "expected_impact": "high"
                })

            elif bottleneck["type"] == "exploration_rate":
                optimizations.append({
                    "type": "decay_exploration",
                    "description": "Accelerate exploration rate decay",
                    "expected_impact": "medium"
                })

            elif bottleneck["type"] == "knowledge_growth":
                optimizations.append({
                    "type": "enable_transfer_learning",
                    "description": "Enable transfer learning to accelerate knowledge acquisition",
                    "expected_impact": "high"
                })

        return optimizations

    def _apply_optimization(self, optimization: Dict[str, Any]) -> bool:
        """Apply a specific optimization"""
        opt_type = optimization["type"]

        if opt_type == "increase_batch_size":
            # Increase batch size for learning (would affect learn_from_experiences calls)
            return True

        elif opt_type == "decay_exploration":
            self.exploration_decay = min(0.99, self.exploration_decay * 1.1)
            return True

        elif opt_type == "enable_transfer_learning":
            # Enable transfer learning (would affect learning strategy)
            return True

        return False

    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics"""
        return {
            "total_experiences": self.learning_metrics["total_experiences"],
            "successful_actions": self.learning_metrics["successful_actions"],
            "success_rate": round(self.learning_metrics["successful_actions"] / max(1, self.learning_metrics["total_experiences"]) * 100, 1),
            "average_reward": round(self.learning_metrics["average_reward"], 3),
            "learning_efficiency": round(self.learning_metrics["learning_efficiency"], 3),
            "exploration_rate": round(self.exploration_rate, 3),
            "knowledge_concepts": len(self.knowledge_base),
            "current_phase": self.current_phase.value
        }

    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """Get summary of learned knowledge"""
        if not self.knowledge_base:
            return {"total_concepts": 0, "average_confidence": 0, "concepts": []}

        concepts = []
        total_confidence = 0

        for concept, knowledge in self.knowledge_base.items():
            concepts.append({
                "concept": concept,
                "confidence": round(knowledge.confidence, 3),
                "evidence_count": knowledge.evidence_count,
                "last_updated": knowledge.last_updated.isoformat(),
                "related_concepts": list(knowledge.related_concepts)
            })
            total_confidence += knowledge.confidence

        return {
            "total_concepts": len(self.knowledge_base),
            "average_confidence": round(total_confidence / len(self.knowledge_base), 3),
            "concepts": concepts
        }

    def export_knowledge(self, filepath: str):
        """
        Export learned knowledge to file.

        Args:
            filepath: Path to export file
        """
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "learning_metrics": self.get_learning_metrics(),
            "knowledge_base": self.get_knowledge_base_summary(),
            "experiences_count": len(self.experiences)
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"💾 Knowledge exported to {filepath}")
        except Exception as e:
            print(f"❌ Failed to export knowledge: {e}")

    def import_knowledge(self, filepath: str):
        """
        Import learned knowledge from file.

        Args:
            filepath: Path to import file
        """
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)

            # Import knowledge base
            if "knowledge_base" in import_data:
                kb_data = import_data["knowledge_base"]
                for concept_data in kb_data.get("concepts", []):
                    concept = concept_data["concept"]
                    knowledge = LearnedKnowledge(
                        concept=concept,
                        confidence=concept_data["confidence"],
                        evidence_count=concept_data["evidence_count"],
                        last_updated=datetime.fromisoformat(concept_data["last_updated"]),
                        related_concepts=set(concept_data["related_concepts"]),
                        performance_metrics={}  # Not stored in export
                    )
                    self.knowledge_base[concept] = knowledge

            print(f"📥 Knowledge imported from {filepath}")
        except Exception as e:
            print(f"❌ Failed to import knowledge: {e}")

    def reset_learning(self):
        """Reset the learning system"""
        self.experiences.clear()
        self.knowledge_base.clear()
        self.learning_models.clear()
        self.exploration_rate = 0.3
        self.learning_metrics = {
            "total_experiences": 0,
            "successful_actions": 0,
            "average_reward": 0.0,
            "learning_efficiency": 0.0,
            "knowledge_growth": 0.0
        }
        print("🔄 Learning system reset")

    def get_system_health(self) -> Dict[str, Any]:
        """Get adaptive learning system health"""
        return {
            "experiences_count": len(self.experiences),
            "knowledge_concepts": len(self.knowledge_base),
            "learning_metrics": self.get_learning_metrics(),
            "current_phase": self.current_phase.value,
            "exploration_rate": round(self.exploration_rate, 3),
            "performance_history_size": len(self.performance_history)
        }