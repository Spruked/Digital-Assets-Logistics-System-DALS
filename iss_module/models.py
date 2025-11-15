"""
Pydantic and Dataclass models for the Digital Asset Logistics System (DALS).
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field

from .core.utils import get_stardate, format_timestamp

# --- DALS API Models ---

class DigitalAssetAssignmentRequest(BaseModel):
    asset_type: Literal["FEATURE", "EPIC", "BUILD", "SERVICE", "ARTIFACT"] = Field(
        ..., description="The type of digital asset being tracked (e.g., FEATURE, BUILD)."
    )
    project_id: str = Field(
        ..., min_length=2, max_length=50, description="The Project ID or Component Type (e.g., 'Core-API')."
    )
    source_reference: str = Field(
        ..., min_length=4, max_length=128, description="The Version Tag, Commit Hash, or Source ID (e.g., 'v1.1.0', 'a4b2c8d9')."
    )
    parent_asset_id: Optional[str] = Field(
        None, description="The Asset ID of the parent item (e.g., the Epic containing this Feature)."
    )

class DigitalAssetAssignmentResponse(BaseModel):
    asset_id: str = Field(description="The newly generated and logged unique Asset ID.")
    iss_timestamp: str = Field(description="The time-anchored timestamp of assignment.")
    audit_hash: str = Field(description="A comprehensive hash of the assignment record.")
    status: str = Field(description="The status of the operation.")
    parent_asset_id: Optional[str] = Field(None, description="The parent asset's ID (if applicable).")

class AssetDependency(BaseModel):
    dependency_name: str = Field(..., description="Name of the dependency (e.g., 'Auth-Service', 'React-v18').")
    asset_id: str = Field(..., description="The Asset ID or external identifier for this dependency.")
    status: str = Field(default="LINKED", max_length=50)

class AssetDeploymentCreate(BaseModel):
    asset_id: str = Field(..., description="The main Asset ID for the component.")
    project_id: str = Field(..., description="The Project ID associated with the asset.")
    deployment_environment: Optional[str] = Field(None, max_length=100, description="The environment (e.g., 'Staging', 'Prod-EU').")
    dependencies: Optional[List[AssetDependency]] = Field(default_factory=list, description="List of dependencies and their Asset IDs.")

class AssetStatusUpdate(BaseModel):
    new_status: Literal["IN_PROGRESS", "READY_FOR_DEPLOY", "DEPLOYED", "RETIRED", "FAILED_AUDIT"] = Field(
        ..., description="The new lifecycle status of the asset."
    )
    update_details: Optional[str] = Field(None, max_length=1000)
    dependencies_update: Optional[List[AssetDependency]] = Field(None, description="Updates/changes to asset dependencies.")

class AssetRecordResponse(BaseModel):
    id: str
    timestamp: str
    stardate: float
    asset_id: str
    project_id: str
    status: str
    deployment_environment: Optional[str]
    dependencies: List[AssetDependency]
    history: List[Dict[str, Any]]

class SystemStatusResponse(BaseModel):
    status: str
    uptime: Optional[str]
    active_modules: List[str]
    current_time: str
    stardate: float
    total_tracked_assets: int

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

class LoginResponse(BaseModel):
    success: bool = Field(description="Whether login was successful")
    token: Optional[str] = Field(None, description="Authentication token for subsequent requests")
    message: str = Field(description="Login result message")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if login successful")

# --- Inventory Manager Dataclass ---

@dataclass
class UnitRecord:
    """Data class for a single tracked digital asset."""
    id: str  # Internal record ID, usually the asset_id
    asset_id: str
    project_id: str  # Formerly model_id
    timestamp: str = field(default_factory=format_timestamp)
    stardate: float = field(default_factory=get_stardate)
    status: str = "PENDING"
    
    # Deployment & Dependency Info
    deployment_environment: Optional[str] = None
    dependencies: List[AssetDependency] = field(default_factory=list)
    
    # Lineage & Audit Trail
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling nested dataclasses."""
        from dataclasses import asdict
        data = asdict(self)
        # Pydantic models in the list need to be converted to dicts manually
        data['dependencies'] = [dep.dict() for dep in self.dependencies]
        return data
