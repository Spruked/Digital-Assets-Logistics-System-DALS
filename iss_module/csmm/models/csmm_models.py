"""
CSMM Data Models

Pydantic models for Caleon Self-Maintenance Module data structures.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class HealthStatus(Enum):
    """System health status levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    UNKNOWN = "unknown"

class ComponentStatus(Enum):
    """Component operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class RepairStatus(Enum):
    """Repair action status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DiagnosticSeverity(Enum):
    """Diagnostic issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SystemHealth(BaseModel):
    """Overall system health assessment - DALS-001 compliant"""
    timestamp: str = Field(..., description="ISO timestamp of health check")
    stardate: str = Field(..., description="Canonical DALS stardate")
    overall_score: int = Field(..., description="Health score 0-100, or 0 if inactive")
    component_health: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Component-specific health data")
    issues_detected: int = Field(0, description="Number of detected issues")

class ComponentIssue(BaseModel):
    """Individual component issue"""
    component: str = Field(..., description="Component name")
    issue_type: str = Field(..., description="Type of issue detected")
    severity: DiagnosticSeverity = Field(..., description="Issue severity level")
    description: str = Field(..., description="Human-readable description")
    recommended_action: str = Field(..., description="Recommended repair action")
    detected_at: str = Field(..., description="When issue was detected")

class DiagnosticResult(BaseModel):
    """Results from diagnostic operations"""
    diagnostic_id: str = Field(..., description="Unique diagnostic run ID")
    timestamp: str = Field(..., description="When diagnostic was run")
    target_component: Optional[str] = Field(None, description="Specific component targeted, or None for full system")
    issues_found: bool = Field(..., description="Whether any issues were detected")
    issues: List[ComponentIssue] = Field(default_factory=list, description="List of detected issues")
    system_health: SystemHealth = Field(..., description="Overall system health at time of diagnostic")
    duration_seconds: float = Field(..., description="How long diagnostic took")

class RepairAction(BaseModel):
    """Individual repair action"""
    id: str = Field(..., description="Unique repair action ID")
    target_component: str = Field(..., description="Component to repair")
    action_type: str = Field(..., description="Type of repair action")
    priority: DiagnosticSeverity = Field(..., description="Repair priority")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    created_at: str = Field(..., description="When repair was created")
    started_at: Optional[str] = Field(None, description="When repair started")
    completed_at: Optional[str] = Field(None, description="When repair completed")
    status: RepairStatus = Field(RepairStatus.PENDING, description="Current repair status")
    result: Optional[Dict[str, Any]] = Field(None, description="Repair execution results")
    error_message: Optional[str] = Field(None, description="Error message if repair failed")

class LearningPattern(BaseModel):
    """Learned pattern from repair operations"""
    pattern_id: str = Field(..., description="Unique pattern ID")
    issue_type: str = Field(..., description="Type of issue this pattern addresses")
    successful_repairs: int = Field(..., description="Number of successful applications")
    failed_repairs: int = Field(..., description="Number of failed applications")
    average_resolution_time: float = Field(..., description="Average time to resolve")
    confidence_score: float = Field(..., description="Confidence in pattern effectiveness 0-1")
    last_updated: str = Field(..., description="When pattern was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional pattern metadata")

class CSMMStatus(BaseModel):
    """CSMM system status - DALS-001 compliant"""
    active: bool = Field(..., description="Whether CSMM is currently active")
    health_score: int = Field(0, description="Current system health score, or 0 if inactive")
    last_diagnostic: Optional[DiagnosticResult] = Field(None, description="Last diagnostic run")
    active_repairs: int = Field(0, description="Number of currently active repairs")
    learned_patterns: int = Field(0, description="Number of learned repair patterns")

class CSMMConfig(BaseModel):
    """CSMM configuration settings"""
    diagnostic_interval: int = Field(60, description="Seconds between diagnostic runs")
    max_concurrent_repairs: int = Field(3, description="Maximum concurrent repair operations")
    learning_enabled: bool = Field(True, description="Whether learning is enabled")
    emergency_mode: bool = Field(False, description="Emergency operation mode")
    founder_override_enabled: bool = Field(True, description="Founder override capability")

class RepairChain(BaseModel):
    """Chain of related repair actions"""
    chain_id: str = Field(..., description="Unique chain ID")
    trigger_issue: ComponentIssue = Field(..., description="Original issue that triggered the chain")
    repairs: List[RepairAction] = Field(default_factory=list, description="Sequence of repair actions")
    status: str = Field(..., description="Overall chain status")
    created_at: str = Field(..., description="When chain was created")
    completed_at: Optional[str] = Field(None, description="When chain completed")
    success_rate: float = Field(0.0, description="Success rate of repairs in chain")

class DiagnosticRule(BaseModel):
    """Diagnostic rule for automated issue detection"""
    rule_id: str = Field(..., description="Unique rule ID")
    component: str = Field(..., description="Component this rule applies to")
    condition: str = Field(..., description="Condition that triggers this rule")
    action: str = Field(..., description="Recommended action")
    confidence: float = Field(..., description="Confidence score 0-1")
    created_at: str = Field(..., description="When rule was created")
    last_updated: str = Field(..., description="When rule was last updated")
    common_errors: List[str] = Field(default_factory=list, description="Common error messages for this rule")