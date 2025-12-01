# module_blueprints.py

"""
Module Blueprints - Dynamic Component Registration System

This module provides a blueprint system for registering and managing
dynamic components in the vault system, enabling plug-and-play
functionality and self-healing capabilities.
"""

import inspect
import importlib
import json
import os
from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime
from enum import Enum


class ComponentStatus(Enum):
    """Status of a component"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FAILED = "failed"
    UNREGISTERED = "unregistered"


class ComponentType(Enum):
    """Types of components that can be registered"""
    VAULT = "vault"
    GLYPH = "glyph"
    REFLECTION = "reflection"
    TELEMETRY = "telemetry"
    SYNC = "sync"
    SECURITY = "security"
    LIFECYCLE = "lifecycle"
    UTILITY = "utility"


class ComponentBlueprint:
    """
    Blueprint for a component, containing all metadata and configuration.
    """

    def __init__(self, name: str, component_type: ComponentType,
                 class_ref: Type, config: Optional[Dict[str, Any]] = None,
                 dependencies: Optional[List[str]] = None, version: str = "1.0.0"):
        """
        Initialize a component blueprint.

        Args:
            name: Component name
            component_type: Type of component
            class_ref: Reference to the component class
            config: Configuration parameters
            dependencies: List of component dependencies
            version: Component version
        """
        self.name = name
        self.component_type = component_type
        self.class_ref = class_ref
        self.config = config or {}
        self.dependencies = dependencies or []
        self.version = version
        self.registered_at = datetime.now()

        # Extract class information
        self.class_name = class_ref.__name__
        self.module_name = class_ref.__module__

        # Validate blueprint
        self._validate_blueprint()

    def _validate_blueprint(self):
        """Validate the blueprint configuration"""
        required_methods = []

        # Type-specific validation
        if self.component_type == ComponentType.VAULT:
            required_methods = ["store", "retrieve"]
        elif self.component_type == ComponentType.GLYPH:
            required_methods = ["generate_glyph"]
        elif self.component_type == ComponentType.REFLECTION:
            required_methods = ["add_reflection"]
        elif self.component_type == ComponentType.TELEMETRY:
            required_methods = ["record_event"]
        elif self.component_type == ComponentType.SYNC:
            required_methods = ["sync"]
        elif self.component_type == ComponentType.SECURITY:
            required_methods = ["validate", "encrypt"]
        elif self.component_type == ComponentType.LIFECYCLE:
            required_methods = ["start_component", "stop_component"]

        # Check if class has required methods
        for method in required_methods:
            if not hasattr(self.class_ref, method):
                raise ValueError(f"Component {self.name} missing required method: {method}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert blueprint to dictionary"""
        return {
            "name": self.name,
            "component_type": self.component_type.value,
            "class_name": self.class_name,
            "module_name": self.module_name,
            "config": self.config,
            "dependencies": self.dependencies,
            "version": self.version,
            "registered_at": self.registered_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentBlueprint':
        """Create blueprint from dictionary"""
        # Import the class dynamically
        module = importlib.import_module(data["module_name"])
        class_ref = getattr(module, data["class_name"])

        blueprint = cls(
            name=data["name"],
            component_type=ComponentType(data["component_type"]),
            class_ref=class_ref,
            config=data.get("config", {}),
            dependencies=data.get("dependencies", []),
            version=data.get("version", "1.0.0")
        )

        blueprint.registered_at = datetime.fromisoformat(data["registered_at"])
        return blueprint


class ComponentInstance:
    """
    Represents an instantiated component with its lifecycle state.
    """

    def __init__(self, blueprint: ComponentBlueprint, instance_id: str):
        """
        Initialize a component instance.

        Args:
            blueprint: Component blueprint
            instance_id: Unique instance identifier
        """
        self.blueprint = blueprint
        self.instance_id = instance_id
        self.status = ComponentStatus.REGISTERED
        self.instance = None
        self.created_at = datetime.now()
        self.last_health_check = None
        self.error_count = 0
        self.start_count = 0

    def instantiate(self) -> bool:
        """
        Instantiate the component.

        Returns:
            Instantiation success status
        """
        try:
            self.status = ComponentStatus.INITIALIZING

            # Create instance with config
            if self.blueprint.config:
                self.instance = self.blueprint.class_ref(**self.blueprint.config)
            else:
                self.instance = self.blueprint.class_ref()

            self.status = ComponentStatus.ACTIVE
            self.start_count += 1
            return True

        except Exception as e:
            self.status = ComponentStatus.FAILED
            self.error_count += 1
            print(f"❌ Failed to instantiate {self.blueprint.name}: {e}")
            return False

    def suspend(self) -> bool:
        """
        Suspend the component.

        Returns:
            Suspension success status
        """
        if self.status != ComponentStatus.ACTIVE:
            return False

        try:
            if hasattr(self.instance, 'suspend'):
                self.instance.suspend()
            self.status = ComponentStatus.SUSPENDED
            return True
        except Exception as e:
            print(f"⚠️  Error suspending {self.blueprint.name}: {e}")
            return False

    def resume(self) -> bool:
        """
        Resume the component.

        Returns:
            Resume success status
        """
        if self.status != ComponentStatus.SUSPENDED:
            return False

        try:
            if hasattr(self.instance, 'resume'):
                self.instance.resume()
            self.status = ComponentStatus.ACTIVE
            return True
        except Exception as e:
            print(f"⚠️  Error resuming {self.blueprint.name}: {e}")
            return False

    def destroy(self) -> bool:
        """
        Destroy the component instance.

        Returns:
            Destruction success status
        """
        try:
            if self.instance is not None:
                if hasattr(self.instance, 'cleanup'):
                    self.instance.cleanup()
                elif hasattr(self.instance, 'close'):
                    self.instance.close()

            self.instance = None
            self.status = ComponentStatus.UNREGISTERED
            return True
        except Exception as e:
            print(f"⚠️  Error destroying {self.blueprint.name}: {e}")
            return False

    def health_check(self) -> bool:
        """
        Perform health check on the component.

        Returns:
            Health status
        """
        if self.status != ComponentStatus.ACTIVE or not self.instance:
            return False

        try:
            if hasattr(self.instance, 'health_check'):
                result = self.instance.health_check()
                self.last_health_check = datetime.now()
                return result
            else:
                # Basic health check - just verify instance exists
                self.last_health_check = datetime.now()
                return True
        except Exception as e:
            self.error_count += 1
            print(f"⚠️  Health check failed for {self.blueprint.name}: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "instance_id": self.instance_id,
            "blueprint": self.blueprint.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "error_count": self.error_count,
            "start_count": self.start_count,
            "has_instance": self.instance is not None
        }


class BlueprintManager:
    """
    Manager for component blueprints and instances.

    Provides registration, instantiation, and lifecycle management
    for dynamic components.
    """

    def __init__(self, storage_path: str = "./blueprints"):
        """
        Initialize the blueprint manager.

        Args:
            storage_path: Path to store blueprint data
        """
        self.storage_path = storage_path
        self._ensure_storage_directory()

        # Blueprint storage
        self.blueprints: Dict[str, ComponentBlueprint] = {}
        self.instances: Dict[str, ComponentInstance] = {}

        # Dependency resolution
        self.dependency_graph: Dict[str, List[str]] = {}

        # Load existing blueprints
        self._load_blueprints()

        print(f"📋 Blueprint Manager initialized at {storage_path}")

    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _load_blueprints(self):
        """Load existing blueprints from disk"""
        blueprints_file = os.path.join(self.storage_path, "blueprints.json")

        if os.path.exists(blueprints_file):
            try:
                with open(blueprints_file, 'r') as f:
                    data = json.load(f)

                for blueprint_data in data.get("blueprints", []):
                    blueprint = ComponentBlueprint.from_dict(blueprint_data)
                    self.blueprints[blueprint.name] = blueprint

                print(f"📚 Loaded {len(self.blueprints)} blueprints")

            except Exception as e:
                print(f"⚠️  Warning: Could not load blueprints: {e}")

    def _save_blueprints(self):
        """Save blueprints to disk"""
        blueprints_file = os.path.join(self.storage_path, "blueprints.json")

        data = {
            "blueprints": [bp.to_dict() for bp in self.blueprints.values()],
            "last_updated": datetime.now().isoformat()
        }

        with open(blueprints_file, 'w') as f:
            json.dump(data, f, indent=2)

    def register_blueprint(self, name: str, component_type: ComponentType,
                          class_ref: Type, config: Dict[str, Any] = None,
                          dependencies: List[str] = None, version: str = "1.0.0") -> bool:
        """
        Register a new component blueprint.

        Args:
            name: Component name
            component_type: Type of component
            class_ref: Component class reference
            config: Configuration parameters
            dependencies: Component dependencies
            version: Component version

        Returns:
            Registration success status
        """
        try:
            blueprint = ComponentBlueprint(
                name=name,
                component_type=component_type,
                class_ref=class_ref,
                config=config,
                dependencies=dependencies,
                version=version
            )

            self.blueprints[name] = blueprint
            self.dependency_graph[name] = dependencies or []

            self._save_blueprints()

            print(f"✅ Registered blueprint: {name} ({component_type.value})")
            return True

        except Exception as e:
            print(f"❌ Failed to register blueprint {name}: {e}")
            return False

    def unregister_blueprint(self, name: str) -> bool:
        """
        Unregister a component blueprint.

        Args:
            name: Component name

        Returns:
            Unregistration success status
        """
        if name not in self.blueprints:
            return False

        # Check if any instances exist
        active_instances = [
            instance_id for instance_id, instance in self.instances.items()
            if instance.blueprint.name == name and instance.status != ComponentStatus.UNREGISTERED
        ]

        if active_instances:
            print(f"⚠️  Cannot unregister {name}: {len(active_instances)} active instances")
            return False

        del self.blueprints[name]
        if name in self.dependency_graph:
            del self.dependency_graph[name]

        self._save_blueprints()
        print(f"✅ Unregistered blueprint: {name}")
        return True

    def instantiate_component(self, blueprint_name: str,
                             instance_id: str = None) -> Optional[str]:
        """
        Instantiate a component from a blueprint.

        Args:
            blueprint_name: Name of the blueprint
            instance_id: Optional instance ID

        Returns:
            Instance ID or None if failed
        """
        if blueprint_name not in self.blueprints:
            print(f"❌ Blueprint not found: {blueprint_name}")
            return None

        blueprint = self.blueprints[blueprint_name]

        # Check dependencies
        if not self._check_dependencies(blueprint_name):
            print(f"❌ Dependencies not satisfied for {blueprint_name}")
            return None

        # Generate instance ID
        if not instance_id:
            instance_id = f"{blueprint_name}_{int(datetime.now().timestamp())}"

        # Check for duplicate instance ID
        if instance_id in self.instances:
            print(f"❌ Instance ID already exists: {instance_id}")
            return None

        # Create instance
        instance = ComponentInstance(blueprint, instance_id)
        self.instances[instance_id] = instance

        # Instantiate the component
        if instance.instantiate():
            print(f"✅ Instantiated component: {instance_id}")
            return instance_id
        else:
            # Clean up failed instance
            del self.instances[instance_id]
            return None

    def destroy_component(self, instance_id: str) -> bool:
        """
        Destroy a component instance.

        Args:
            instance_id: Instance ID

        Returns:
            Destruction success status
        """
        if instance_id not in self.instances:
            return False

        instance = self.instances[instance_id]

        if instance.destroy():
            print(f"✅ Destroyed component: {instance_id}")
            return True
        else:
            return False

    def get_component_instance(self, instance_id: str) -> Optional[Any]:
        """
        Get the actual component instance.

        Args:
            instance_id: Instance ID

        Returns:
            Component instance or None
        """
        instance = self.instances.get(instance_id)
        if instance and instance.status == ComponentStatus.ACTIVE:
            return instance.instance
        return None

    def list_blueprints(self, component_type: ComponentType = None) -> List[Dict[str, Any]]:
        """
        List registered blueprints.

        Args:
            component_type: Optional type filter

        Returns:
            List of blueprint information
        """
        blueprints = self.blueprints.values()

        if component_type:
            blueprints = [bp for bp in blueprints if bp.component_type == component_type]

        return [bp.to_dict() for bp in blueprints]

    def list_instances(self, blueprint_name: str = None,
                      status: ComponentStatus = None) -> List[Dict[str, Any]]:
        """
        List component instances.

        Args:
            blueprint_name: Optional blueprint name filter
            status: Optional status filter

        Returns:
            List of instance information
        """
        instances = self.instances.values()

        if blueprint_name:
            instances = [inst for inst in instances if inst.blueprint.name == blueprint_name]

        if status:
            instances = [inst for inst in instances if inst.status == status]

        return [inst.get_info() for inst in instances]

    def _check_dependencies(self, blueprint_name: str) -> bool:
        """Check if dependencies are satisfied"""
        dependencies = self.dependency_graph.get(blueprint_name, [])

        for dep in dependencies:
            # Check if dependency blueprint exists
            if dep not in self.blueprints:
                print(f"❌ Missing dependency blueprint: {dep}")
                return False

            # Check if at least one instance of dependency is active
            dep_instances = [
                inst for inst in self.instances.values()
                if inst.blueprint.name == dep and inst.status == ComponentStatus.ACTIVE
            ]

            if not dep_instances:
                print(f"❌ No active instance of dependency: {dep}")
                return False

        return True

    def resolve_dependencies(self, blueprint_name: str) -> List[str]:
        """
        Resolve dependency order for a blueprint.

        Args:
            blueprint_name: Blueprint name

        Returns:
            Ordered list of blueprints to instantiate
        """
        if blueprint_name not in self.dependency_graph:
            return []

        resolved = []
        visiting = set()

        def visit(name):
            if name in visiting:
                raise ValueError(f"Circular dependency detected: {name}")
            if name in resolved:
                return

            visiting.add(name)

            for dep in self.dependency_graph.get(name, []):
                visit(dep)

            visiting.remove(name)
            resolved.append(name)

        visit(blueprint_name)
        return resolved[:-1]  # Exclude the target blueprint itself

    def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all instances.

        Returns:
            Health check results
        """
        results = {
            "total_instances": len(self.instances),
            "healthy": 0,
            "unhealthy": 0,
            "failed": 0,
            "details": []
        }

        for instance in self.instances.values():
            is_healthy = instance.health_check()

            if is_healthy:
                results["healthy"] += 1
            else:
                results["unhealthy"] += 1
                if instance.error_count > 5:
                    results["failed"] += 1

            results["details"].append({
                "instance_id": instance.instance_id,
                "blueprint": instance.blueprint.name,
                "healthy": is_healthy,
                "errors": instance.error_count
            })

        return results

    def auto_heal(self) -> Dict[str, Any]:
        """
        Attempt to auto-heal failed components.

        Returns:
            Healing results
        """
        results = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "details": []
        }

        for instance in self.instances.values():
            if instance.status == ComponentStatus.FAILED and instance.error_count <= 10:
                results["attempted"] += 1

                # Try to reinstantiate
                old_instance = instance.instance
                if instance.instantiate():
                    results["successful"] += 1
                    results["details"].append({
                        "instance_id": instance.instance_id,
                        "action": "reinstatiated",
                        "success": True
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "instance_id": instance.instance_id,
                        "action": "reinstatiation_failed",
                        "success": False
                    })

        return results

    def get_blueprint_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a blueprint"""
        blueprint = self.blueprints.get(name)
        if not blueprint:
            return None

        return {
            "basic_info": blueprint.to_dict(),
            "instance_count": len([inst for inst in self.instances.values()
                                 if inst.blueprint.name == name]),
            "active_instances": len([inst for inst in self.instances.values()
                                   if inst.blueprint.name == name and
                                   inst.status == ComponentStatus.ACTIVE]),
            "dependencies_satisfied": self._check_dependencies(name)
        }

    def export_blueprints(self, filepath: str) -> bool:
        """
        Export all blueprints to a file.

        Args:
            filepath: Export file path

        Returns:
            Export success status
        """
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "blueprints": [bp.to_dict() for bp in self.blueprints.values()],
                "instances": [inst.get_info() for inst in self.instances.values()],
                "dependency_graph": self.dependency_graph
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def import_blueprints(self, filepath: str) -> bool:
        """
        Import blueprints from a file.

        Args:
            filepath: Import file path

        Returns:
            Import success status
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            imported_count = 0
            for blueprint_data in data.get("blueprints", []):
                try:
                    blueprint = ComponentBlueprint.from_dict(blueprint_data)
                    self.blueprints[blueprint.name] = blueprint
                    imported_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to import blueprint {blueprint_data.get('name')}: {e}")

            if imported_count > 0:
                self._save_blueprints()

            print(f"✅ Imported {imported_count} blueprints")
            return True

        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False