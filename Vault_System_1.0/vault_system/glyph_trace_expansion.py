# glyph_trace_expansion.py

"""
Glyph Trace Expansion - Reasoning Path Tracking System

This module provides comprehensive reasoning path tracking through glyph traces,
enabling auditability and analysis of decision-making processes in the vault system.
"""

import json
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict
from enum import Enum
from vault_core.glyph_generator import GlyphGenerator, GlyphType


class ReasoningStep(Enum):
    """Steps in the reasoning process"""
    SEED_ACTIVATION = "seed_activation"
    PRIOR_ANALYSIS = "prior_analysis"
    EVIDENCE_INTEGRATION = "evidence_integration"
    HYPOTHESIS_FORMATION = "hypothesis_formation"
    PATTERN_RECOGNITION = "pattern_recognition"
    DECISION_SYNTHESIS = "decision_synthesis"
    VALIDATION_CHECK = "validation_check"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"


class TraceNode:
    """
    A node in the reasoning trace graph.
    """

    def __init__(self, step: ReasoningStep, component: str,
                 data: Dict[str, Any], glyph_id: Optional[str] = None):
        """
        Initialize a trace node.

        Args:
            step: Reasoning step this node represents
            component: Component that created this node
            data: Data associated with this step
            glyph_id: Associated glyph identifier
        """
        self.step = step
        self.component = component
        self.data = data
        self.glyph_id = glyph_id
        self.timestamp = datetime.now()
        self.node_id = f"node_{int(time.time()*1000000)}"

        # Graph connections
        self.parents: List[str] = []
        self.children: List[str] = []

        # Metadata
        self.confidence_score = data.get("confidence", 0.5)
        self.processing_time = data.get("processing_time", 0.0)
        self.evidence_strength = data.get("evidence_strength", 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "node_id": self.node_id,
            "step": self.step.value,
            "component": self.component,
            "data": self.data,
            "glyph_id": self.glyph_id,
            "timestamp": self.timestamp.isoformat(),
            "parents": self.parents,
            "children": self.children,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "evidence_strength": self.evidence_strength
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceNode':
        """Create node from dictionary"""
        glyph_id = data.get("glyph_id")
        if glyph_id is None:
            glyph_id = ""
        node = cls(
            step=ReasoningStep(data["step"]),
            component=data["component"],
            data=data["data"],
            glyph_id=glyph_id
        )
        node.node_id = data["node_id"]
        node.timestamp = datetime.fromisoformat(data["timestamp"])
        node.parents = data.get("parents", [])
        node.children = data.get("children", [])
        node.confidence_score = data.get("confidence_score", 0.5)
        node.processing_time = data.get("processing_time", 0.0)
        node.evidence_strength = data.get("evidence_strength", 0.0)
        return node


class ReasoningPath:
    """
    A complete reasoning path with trace nodes and analysis.
    """

    def __init__(self, path_id: str, initial_query: str):
        """
        Initialize a reasoning path.

        Args:
            path_id: Unique path identifier
            initial_query: The initial reasoning query
        """
        self.path_id = path_id
        self.initial_query = initial_query
        self.created_at = datetime.now()
        self.completed_at = None

        # Path structure
        self.nodes: Dict[str, TraceNode] = {}
        self.root_nodes: List[str] = []
        self.leaf_nodes: List[str] = []

        # Path metadata
        self.total_processing_time = 0.0
        self.average_confidence = 0.0
        self.evidence_strength = 0.0
        self.decision_outcome = None
        self.verdict_confidence = 0.0

        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}

    def add_node(self, node: TraceNode, parent_ids: Optional[List[str]] = None):
        """
        Add a node to the reasoning path.

        Args:
            node: Node to add
            parent_ids: IDs of parent nodes
        """
        self.nodes[node.node_id] = node

        # Set up parent-child relationships
        if parent_ids:
            for parent_id in parent_ids:
                if parent_id in self.nodes:
                    parent = self.nodes[parent_id]
                    if node.node_id not in parent.children:
                        parent.children.append(node.node_id)
                    if parent_id not in node.parents:
                        node.parents.append(parent_id)

        # Update root and leaf nodes
        if not node.parents:
            if node.node_id not in self.root_nodes:
                self.root_nodes.append(node.node_id)
        else:
            # Remove from roots if it was one
            if node.node_id in self.root_nodes:
                self.root_nodes.remove(node.node_id)

        # Update leaf nodes
        self._update_leaf_nodes()

    def _update_leaf_nodes(self):
        """Update the list of leaf nodes"""
        self.leaf_nodes = [
            node_id for node_id in self.nodes.keys()
            if not self.nodes[node_id].children
        ]

    def complete_path(self, decision_outcome: Any, verdict_confidence: float,
                     processing_time: float):
        """
        Complete the reasoning path.

        Args:
            decision_outcome: Final decision outcome
            verdict_confidence: Confidence in the verdict
            processing_time: Total processing time
        """
        self.completed_at = datetime.now()
        self.decision_outcome = decision_outcome
        self.verdict_confidence = verdict_confidence
        self.total_processing_time = processing_time

        # Calculate path statistics
        self._calculate_path_statistics()

    def _calculate_path_statistics(self):
        """Calculate statistics for the reasoning path"""
        if not self.nodes:
            return

        confidences = [node.confidence_score for node in self.nodes.values()]
        evidence_strengths = [node.evidence_strength for node in self.nodes.values()]

        self.average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        self.evidence_strength = sum(evidence_strengths) / len(evidence_strengths) if evidence_strengths else 0.0

    def get_path_depth(self) -> int:
        """Get the maximum depth of the reasoning path"""
        if not self.nodes:
            return 0


        def get_node_depth(node_id: str, visited: Optional[Set[str]] = None) -> int:
            if visited is None:
                visited = set()

            if node_id in visited:
                return 0  # Avoid cycles

            visited.add(node_id)
            node = self.nodes[node_id]

            if not node.children:
                return 1

            return 1 + max(get_node_depth(child, visited.copy()) for child in node.children)

        return max(get_node_depth(root) for root in self.root_nodes) if self.root_nodes else 0

    def get_critical_path(self) -> List[str]:
        """Get the critical path (longest chain of reasoning)"""
        if not self.nodes:
            return []

        def find_longest_path(node_id: str, visited: Optional[Set[str]] = None) -> List[str]:
            if visited is None:
                visited = set()

            if node_id in visited:
                return []

            visited.add(node_id)
            node = self.nodes[node_id]

            if not node.children:
                return [node_id]

            longest = []
            for child in node.children:
                path = find_longest_path(child, visited.copy())
                if len(path) > len(longest):
                    longest = path

            return [node_id] + longest

        critical_paths = [find_longest_path(root) for root in self.root_nodes]
        return max(critical_paths, key=len) if critical_paths else []

    def analyze_path(self) -> Dict[str, Any]:
        """Analyze the reasoning path for patterns and insights"""
        if self.path_id in self.analysis_cache:
            return self.analysis_cache[self.path_id]

        analysis = {
            "path_id": self.path_id,
            "total_nodes": len(self.nodes),
            "path_depth": self.get_path_depth(),
            "processing_time": self.total_processing_time,
            "average_confidence": self.average_confidence,
            "evidence_strength": self.evidence_strength,
            "verdict_confidence": self.verdict_confidence,
            "step_distribution": self._analyze_step_distribution(),
            "confidence_progression": self._analyze_confidence_progression(),
            "evidence_accumulation": self._analyze_evidence_accumulation(),
            "critical_path": self.get_critical_path(),
            "bottlenecks": self._identify_bottlenecks(),
            "decision_quality": self._assess_decision_quality()
        }

        self.analysis_cache[self.path_id] = analysis
        return analysis

    def _analyze_step_distribution(self) -> Dict[str, int]:
        """Analyze distribution of reasoning steps"""
        distribution = defaultdict(int)
        for node in self.nodes.values():
            distribution[node.step.value] += 1
        return dict(distribution)

    def _analyze_confidence_progression(self) -> List[float]:
        """Analyze how confidence changes through the path"""
        # Sort nodes by timestamp
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.timestamp)
        return [node.confidence_score for node in sorted_nodes]

    def _analyze_evidence_accumulation(self) -> List[float]:
        """Analyze how evidence strength accumulates"""
        # Sort nodes by timestamp
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.timestamp)
        return [node.evidence_strength for node in sorted_nodes]

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks in reasoning"""
        bottlenecks = []

        for node in self.nodes.values():
            if node.processing_time > 1.0:  # More than 1 second
                bottlenecks.append({
                    "node_id": node.node_id,
                    "step": node.step.value,
                    "processing_time": node.processing_time,
                    "confidence": node.confidence_score
                })

        return sorted(bottlenecks, key=lambda x: x["processing_time"], reverse=True)

    def _assess_decision_quality(self) -> Dict[str, Any]:
        """Assess the quality of the final decision"""
        if not self.completed_at:
            return {"status": "incomplete"}

        quality_score = (
            self.verdict_confidence * 0.4 +
            self.average_confidence * 0.3 +
            self.evidence_strength * 0.3
        )

        # Assess quality based on various factors
        factors = {
            "confidence_alignment": abs(self.verdict_confidence - self.average_confidence),
            "evidence_support": self.evidence_strength,
            "path_depth": self.get_path_depth(),
            "processing_efficiency": 1.0 / (self.total_processing_time + 1),  # Avoid division by zero
        }

        if quality_score > 0.8:
            quality = "excellent"
        elif quality_score > 0.6:
            quality = "good"
        elif quality_score > 0.4:
            quality = "fair"
        else:
            quality = "poor"

        return {
            "quality_score": round(quality_score, 3),
            "quality": quality,
            "factors": factors
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert path to dictionary"""
        return {
            "path_id": self.path_id,
            "initial_query": self.initial_query,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "root_nodes": self.root_nodes,
            "leaf_nodes": self.leaf_nodes,
            "total_processing_time": self.total_processing_time,
            "average_confidence": self.average_confidence,
            "evidence_strength": self.evidence_strength,
            "decision_outcome": self.decision_outcome,
            "verdict_confidence": self.verdict_confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningPath':
        """Create path from dictionary"""
        path = cls(
            path_id=data["path_id"],
            initial_query=data["initial_query"]
        )

        path.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("completed_at"):
            path.completed_at = datetime.fromisoformat(data["completed_at"])

        # Reconstruct nodes
        for node_id, node_data in data.get("nodes", {}).items():
            node = TraceNode.from_dict(node_data)
            path.nodes[node_id] = node

        path.root_nodes = data.get("root_nodes", [])
        path.leaf_nodes = data.get("leaf_nodes", [])
        path.total_processing_time = data.get("total_processing_time", 0.0)
        path.average_confidence = data.get("average_confidence", 0.0)
        path.evidence_strength = data.get("evidence_strength", 0.0)
        path.decision_outcome = data.get("decision_outcome")
        path.verdict_confidence = data.get("verdict_confidence", 0.0)

        return path


class ReasoningGlyphMapper:
    """
    Maps reasoning processes to glyph traces for visualization and analysis.
    """

    def __init__(self, glyph_generator: GlyphGenerator):
        """
        Initialize the reasoning glyph mapper.

        Args:
            glyph_generator: Glyph generator instance
        """
        self.glyph_generator = glyph_generator
        self.active_paths: Dict[str, ReasoningPath] = {}
        self.completed_paths: List[ReasoningPath] = []

        # Path storage
        self.max_completed_paths = 1000  # Keep last 1000 completed paths

        print("🧬 Reasoning Glyph Mapper initialized")

    def start_reasoning_path(self, initial_query: str) -> str:
        """
        Start a new reasoning path.

        Args:
            initial_query: The initial reasoning query

        Returns:
            Path ID
        """
        path_id = f"path_{int(time.time()*1000000)}"
        path = ReasoningPath(path_id, initial_query)
        self.active_paths[path_id] = path

        # Generate initial glyph
        initial_glyph = self.glyph_generator.generate_glyph(
            f"Query: {initial_query}",
            GlyphType.CONCEPT,
            {"path_id": path_id, "step": "initialization"}
        )

        # Add initial node
        initial_node = TraceNode(
            step=ReasoningStep.SEED_ACTIVATION,
            component="reasoning_mapper",
            data={"query": initial_query, "glyph_generated": True},
            glyph_id=initial_glyph["id"]
        )

        path.add_node(initial_node)
        return path_id

    def add_reasoning_step(self, path_id: str, step: ReasoningStep,
                          component: str, data: Dict[str, Any],
                          parent_node_ids: Optional[List[str]] = None) -> Optional[str]:
        """
        Add a reasoning step to an active path.

        Args:
            path_id: Path identifier
            step: Reasoning step
            component: Component adding the step
            data: Step data
            parent_node_ids: Parent node IDs

        Returns:
            Node ID if successful, None otherwise
        """
        if path_id not in self.active_paths:
            print(f"⚠️  Path {path_id} not found or already completed")
            return None

        path = self.active_paths[path_id]

        # Generate glyph for this step
        step_content = f"{step.value}: {data.get('description', str(data))}"
        glyph = self.glyph_generator.generate_glyph(
            step_content,
            GlyphType.REASONING,
            {
                "path_id": path_id,
                "step": step.value,
                "component": component,
                "confidence": data.get("confidence", 0.5)
            }
        )

        # Create trace node
        node = TraceNode(
            step=step,
            component=component,
            data=data,
            glyph_id=glyph["id"]
        )

        # Add to path
        path.add_node(node, parent_node_ids or path.leaf_nodes)

        return node.node_id

    def complete_reasoning_path(self, path_id: str, decision_outcome: Any,
                               verdict_confidence: float, processing_time: Optional[float] = None) -> bool:
        """
        Complete a reasoning path.

        Args:
            path_id: Path identifier
            decision_outcome: Final decision
            verdict_confidence: Confidence in verdict
            processing_time: Total processing time

        Returns:
            Completion success status
        """
        if path_id not in self.active_paths:
            return False

        path = self.active_paths[path_id]

        # Calculate processing time if not provided
        if processing_time is None:
            processing_time = (datetime.now() - path.created_at).total_seconds()

        path.complete_path(decision_outcome, verdict_confidence, processing_time)

        # Move to completed paths
        self.completed_paths.append(path)
        del self.active_paths[path_id]

        # Maintain size limit
        if len(self.completed_paths) > self.max_completed_paths:
            self.completed_paths = self.completed_paths[-self.max_completed_paths:]

        print(f"✅ Completed reasoning path {path_id} with verdict: {decision_outcome}")
        return True

    def get_active_paths(self) -> List[str]:
        """Get list of active path IDs"""
        return list(self.active_paths.keys())

    def get_completed_paths(self, limit: int = 100) -> List[ReasoningPath]:
        """Get recently completed paths"""
        return self.completed_paths[-limit:]

    def get_path(self, path_id: str) -> Optional[ReasoningPath]:
        """Get a specific reasoning path"""
        if path_id in self.active_paths:
            return self.active_paths[path_id]

        for path in self.completed_paths:
            if path.path_id == path_id:
                return path

        return None

    def get_total_paths(self) -> int:
        """Get total number of paths (active + completed)"""
        return len(self.active_paths) + len(self.completed_paths)

    def analyze_reasoning_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns across all completed reasoning paths.

        Returns:
            Pattern analysis results
        """
        if not self.completed_paths:
            return {"status": "no_completed_paths"}

        # Aggregate analysis
        total_paths = len(self.completed_paths)
        avg_confidence = sum(p.verdict_confidence for p in self.completed_paths) / total_paths
        avg_processing_time = sum(p.total_processing_time for p in self.completed_paths) / total_paths
        avg_path_depth = sum(p.get_path_depth() for p in self.completed_paths) / total_paths

        # Decision distribution
        decision_counts = defaultdict(int)
        for path in self.completed_paths:
            decision = str(path.decision_outcome)
            decision_counts[decision] += 1

        # Step usage patterns
        step_usage = defaultdict(int)
        for path in self.completed_paths:
            for node in path.nodes.values():
                step_usage[node.step.value] += 1

        # Quality assessment
        quality_distribution = defaultdict(int)
        for path in self.completed_paths:
            analysis = path.analyze_path()
            quality = analysis["decision_quality"]["quality"]
            quality_distribution[quality] += 1

        return {
            "total_paths_analyzed": total_paths,
            "average_verdict_confidence": round(avg_confidence, 3),
            "average_processing_time": round(avg_processing_time, 3),
            "average_path_depth": round(avg_path_depth, 2),
            "decision_distribution": dict(decision_counts),
            "step_usage_patterns": dict(step_usage),
            "quality_distribution": dict(quality_distribution),
            "most_common_decision": max(decision_counts.items(), key=lambda x: x[1])[0] if decision_counts else None,
            "highest_quality_rate": round((quality_distribution.get("excellent", 0) + quality_distribution.get("good", 0)) / total_paths * 100, 1) if total_paths > 0 else 0
        }

    def get_path_glyphs(self, path_id: str) -> List[Dict[str, Any]]:
        """
        Get all glyphs associated with a reasoning path.

        Args:
            path_id: Path identifier

        Returns:
            List of glyph information
        """
        path = self.get_path(path_id)
        if not path:
            return []

        glyphs = []
        for node in path.nodes.values():
            if node.glyph_id:
                glyph = self.glyph_generator.get_glyph_by_id(node.glyph_id)
                if glyph:
                    glyphs.append({
                        "glyph": glyph,
                        "step": node.step.value,
                        "component": node.component,
                        "confidence": node.confidence_score
                    })

        return glyphs

    def export_path_analysis(self, path_id: str) -> Optional[Dict[str, Any]]:
        """
        Export detailed analysis of a reasoning path.

        Args:
            path_id: Path identifier

        Returns:
            Path analysis data
        """
        path = self.get_path(path_id)
        if not path:
            return None

        analysis = path.analyze_path()

        return {
            "path_info": path.to_dict(),
            "analysis": analysis,
            "glyphs": self.get_path_glyphs(path_id),
            "export_timestamp": datetime.now().isoformat()
        }