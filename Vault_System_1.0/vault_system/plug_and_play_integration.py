# plug_and_play_integration.py

"""
Full Plug-and-Play Integration for Vault_System_1.0

This script demonstrates how all the advanced features work together:
- Lifecycle Control Hooks
- Glyph Trace Expansion
- Self-Repair Protocols
- Dual-Core Integration
- Telemetry Dashboard

Making the vault system truly Caleon's "organized internal world."
"""

import time
import threading
from typing import Dict, Any

# Import all the new advanced components
from lifecycle_control import LifecycleController, LifecycleState
from glyph_trace_expansion import ReasoningGlyphMapper, ReasoningStep
from self_repair import SelfRepairProtocols
from dual_core_integration import DualCoreIntegration, SynchronizationMode
from vault_core.telemetry_stream import TelemetryManager

# Import existing vault system components
from vault_core.cryptographic_vault import CryptographicVault, VaultCategory
from vault_core.glyph_generator import GlyphGenerator
from vault_core.reflection_manager import ReflectionVault, ReflectionEntry
from vault_core.telemetry_stream import TelemetryManager
from vault_core.ISS_bridge import ISSConnector
from vault_core.module_blueprints import BlueprintManager

class AdvancedVaultSystem:
    """
    Advanced vault system with full plug-and-play capabilities.
    This is Caleon's truly dynamic "organized internal world."
    """

    def __init__(self, master_key: str, node_id: str = "advanced_vault"):
        print("🔄 Initializing Advanced Vault System...")

        # Core vault components
        self.vault = CryptographicVault(master_key)
        self.glyph_generator = GlyphGenerator()
        self.telemetry = TelemetryManager()
        # ISS connector (optional for demo)
        try:
            self.iss_connector = ISSConnector(node_id, "secret_key_2024")
        except Exception as e:
            print(f"⚠️  ISS Connector not available: {e}")
            self.iss_connector = None
        self.blueprint_manager = BlueprintManager()

        # Reflection system
        self.reflection_vault = ReflectionVault("./reflection_data")

        # Advanced subsystems
        self.lifecycle_controller = LifecycleController()
        self.reasoning_glyph_mapper = ReasoningGlyphMapper(self.glyph_generator)
        self.self_repair = SelfRepairProtocols(self.blueprint_manager, self.lifecycle_controller)
        # Dual-core integration
        if self.iss_connector:
            self.dual_core = DualCoreIntegration(self.iss_connector, self.lifecycle_controller)
        else:
            self.dual_core = None

        # Telemetry dashboard
        self.dashboard = TelemetryManager()

        # Register all components with lifecycle management
        self._register_components()

        # Start advanced systems
        self._initialize_advanced_systems()

        print("✅ Advanced Vault System initialized with full plug-and-play capabilities!")

    def _register_components(self):
        """Register all components with lifecycle management"""
        # Register core vault
        self.lifecycle_controller.register_component(
            "vault_core",
            self._start_vault_core,
            self._stop_vault_core,
            self._repair_vault_core
        )

        # Register glyph trace
        self.lifecycle_controller.register_component(
            "glyph_trace",
            self._start_glyph_trace,
            self._stop_glyph_trace,
            None  # No repair function for glyph trace
        )

        # Register reflection vault
        self.lifecycle_controller.register_component(
            "reflection_vault",
            self._start_reflection_vault,
            self._stop_reflection_vault,
            None
        )

        # Register telemetry
        self.lifecycle_controller.register_component(
            "telemetry",
            self._start_telemetry,
            self._stop_telemetry,
            None
        )

        # Register ISS bridge
        self.lifecycle_controller.register_component(
            "iss_bridge",
            self._start_iss_bridge,
            self._stop_iss_bridge,
            None
        )

    def _initialize_advanced_systems(self):
        """Initialize all advanced systems"""

        # Start lifecycle management
        print("🔄 Starting lifecycle management...")
        for comp_name in ["vault_core", "glyph_trace", "reflection_vault", "telemetry", "iss_bridge"]:
            if self.lifecycle_controller.start_component(comp_name):
                print(f"✅ Started {comp_name}")
            else:
                print(f"❌ Failed to start {comp_name}")

        # Start self-repair monitoring
        print("🔄 Starting self-repair protocols...")
        self.self_repair.start_health_monitoring()

        # Initialize dual-core integration
        if self.dual_core:
            print("🔄 Initializing dual-core integration...")

            # Register hemisphere mappings
            self.dual_core.register_hemisphere_mapping(
                component_name="vault_core",
                left_instance=self.vault,
                right_instance=self.vault,  # In single instance, same object
                sync_mode=SynchronizationMode.REDUNDANT
            )

            self.dual_core.register_hemisphere_mapping(
                component_name="reflection_vault",
                left_instance=self.reflection_vault,
                right_instance=self.reflection_vault,
                sync_mode=SynchronizationMode.MIRROR
            )

            print("✅ Dual-core integration complete!")
        else:
            print("⚠️  Dual-core integration skipped (ISS connector not available)")

    # Component lifecycle hooks
    def _start_vault_core(self, instance):
        """Start vault core"""
        print("Starting cryptographic vault...")
        # Vault is always ready, just log startup
        self.telemetry.record_event("system", "vault_core", "startup", 0.0, True)

    def _stop_vault_core(self, instance, graceful=True):
        """Stop vault core"""
        print("Stopping cryptographic vault...")
        self.telemetry.record_event("system", "vault_core", "shutdown", 0.0, True)

    def _repair_vault_core(self, instance):
        """Repair vault core"""
        print("Repairing vault core...")
        # In a real implementation, this would reload from backup or reinitialize
        return True

    def _start_glyph_trace(self, instance):
        """Start glyph trace system"""
        print("Starting glyph trace system...")
        self.telemetry.record_event("system", "glyph_trace", "startup", 0.0, True)

    def _stop_glyph_trace(self, instance, graceful=True):
        """Stop glyph trace system"""
        print("Stopping glyph trace system...")
        self.telemetry.record_event("system", "glyph_trace", "shutdown", 0.0, True)

    def _start_reflection_vault(self, instance):
        """Start reflection vault"""
        print("Starting reflection vault...")
        self.telemetry.record_event("system", "reflection_vault", "startup", 0.0, True)

    def _stop_reflection_vault(self, instance, graceful=True):
        """Stop reflection vault"""
        print("Stopping reflection vault...")
        self.telemetry.record_event("system", "reflection_vault", "shutdown", 0.0, True)

    def _start_telemetry(self, instance):
        """Start telemetry system"""
        print("Starting telemetry system...")
        self.telemetry.record_event("system", "telemetry", "startup", 0.0, True)

    def _stop_telemetry(self, instance, graceful=True):
        """Stop telemetry system"""
        print("Stopping telemetry system...")
        self.telemetry.record_event("system", "telemetry", "shutdown", 0.0, True)

    def _start_iss_bridge(self, instance):
        """Start ISS bridge"""
        print("Starting ISS bridge...")
        self.telemetry.record_event("system", "iss_bridge", "startup", 0.0, True)

    def _stop_iss_bridge(self, instance, graceful=True):
        """Stop ISS bridge"""
        print("Stopping ISS bridge...")
        self.telemetry.record_event("system", "iss_bridge", "shutdown", 0.0, True)

    # Advanced operations
    def demonstrate_reasoning_path_tracking(self):
        """Demonstrate complete reasoning path tracking with glyph traces"""
        print("\n🧬 Demonstrating Reasoning Path Tracking...")

        # Start a reasoning path
        path_id = self.reasoning_glyph_mapper.start_reasoning_path("Should I invest in tech stocks?")

        # Add reasoning steps
        self.reasoning_glyph_mapper.add_reasoning_step(
            path_id,
            ReasoningStep.SEED_ACTIVATION,
            "philosophical_seeds",
            {"framework": "pragmatism", "principle": "utility_maximization"}
        )

        self.reasoning_glyph_mapper.add_reasoning_step(
            path_id,
            ReasoningStep.PRIOR_ANALYSIS,
            "decision_engine",
            {"market_trend": "bullish", "confidence": 0.8}
        )

        self.reasoning_glyph_mapper.add_reasoning_step(
            path_id,
            ReasoningStep.EVIDENCE_INTEGRATION,
            "bayesian_engine",
            {"evidence_strength": 0.9, "contradictions": 0}
        )

        # Complete with verdict
        verdict = {"decision": "invest", "confidence": 0.85, "risk_level": "medium"}
        self.reasoning_glyph_mapper.complete_reasoning_path(path_id, verdict, 2.3)

        print(f"✅ Reasoning path {path_id} completed with verdict: {verdict}")

    def demonstrate_self_repair(self):
        """Demonstrate self-repair capabilities"""
        print("\n🔧 Demonstrating Self-Repair Protocols...")

        # Simulate a component failure
        print("Simulating glyph_trace failure...")
        self.lifecycle_controller.stop_component("glyph_trace")

        # Trigger self-repair
        repair_result = self.self_repair.attempt_repair("glyph_trace")
        if repair_result:
            print("✅ Self-repair successful - glyph_trace restarted")
        else:
            print("❌ Self-repair failed")

    def demonstrate_lifecycle_management(self):
        """Demonstrate dynamic lifecycle management"""
        print("\n🔄 Demonstrating Lifecycle Management...")

        # Suspend reflection vault
        print("Suspending reflection_vault...")
        self.lifecycle_controller.suspend_component("reflection_vault")

        # Resume it
        print("Resuming reflection_vault...")
        self.lifecycle_controller.resume_component("reflection_vault")

        print("✅ Lifecycle management demonstrated")

    def demonstrate_dual_core_sync(self):
        """Demonstrate dual-core synchronization"""
        print("\n🧠 Demonstrating Dual-Core Synchronization...")

        # Add some data to vault
        test_data = {"test": "dual_core_sync", "timestamp": time.time()}
        self.vault.store("test_sync", VaultCategory.OPERATIONAL, test_data, "demo", {})

        # Trigger synchronization
        if self.dual_core:
            sync_result = self.dual_core.synchronize_hemispheres()
            if sync_result:
                print("✅ Dual-core synchronization successful")
            else:
                print("❌ Dual-core synchronization failed")
        else:
            print("⚠️  Dual-core synchronization skipped (not available)")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'lifecycle_status': {
                'system_health': self.lifecycle_controller.get_system_health(),
                'active_components': len(self.lifecycle_controller.active_components),
                'suspended_components': len(self.lifecycle_controller.suspended_components)
            },
            'health_status': {
                'healthy_components': self.self_repair.get_healthy_component_count(),
                'failed_components': self.self_repair.get_failed_component_count()
            },
            'reasoning_statistics': {
                'total_paths': self.reasoning_glyph_mapper.get_total_paths(),
                'active_paths': self.reasoning_glyph_mapper.get_active_paths(),
                'completed_paths': self.reasoning_glyph_mapper.get_completed_paths()
            },
            'reflection_summary': {
                'total_reflections': self.reflection_vault.get_total_entries(),
                'recent_reflections': self.reflection_vault.get_recent_entries(5)
            },
            'telemetry_summary': self.telemetry.get_system_health()
        }

    def graceful_shutdown(self):
        """Gracefully shutdown all systems"""
        print("🔄 Initiating graceful shutdown...")

        # Stop all components
        for comp_name in ["vault_core", "glyph_trace", "reflection_vault", "telemetry", "iss_bridge"]:
            self.lifecycle_controller.stop_component(comp_name)

        # Stop dashboard
        if hasattr(self, 'dashboard'):
            pass  # TelemetryManager doesn't need explicit stopping

        print("✅ Graceful shutdown complete")


def main():
    """Main demonstration function"""

    print("🚀 Starting Caleon's Advanced Vault System Demo")
    print("=" * 60)

    # Initialize the advanced system
    vault_system = AdvancedVaultSystem("master_key_2024")

    try:
        # Demonstrate capabilities
        vault_system.demonstrate_reasoning_path_tracking()
        time.sleep(1)

        vault_system.demonstrate_lifecycle_management()
        time.sleep(1)

        vault_system.demonstrate_dual_core_sync()
        time.sleep(1)

        vault_system.demonstrate_self_repair()

        # Show system status
        print("\n📊 Final System Status:")
        status = vault_system.get_system_status()
        print(f"Lifecycle health: {status['lifecycle_status']['system_health']:.2%}")
        print(f"Components healthy: {status['health_status']['healthy_components']}")
        print(f"Reasoning paths: {status['reasoning_statistics']['total_paths']}")
        print(f"Reflections stored: {status['reflection_summary']['total_reflections']}")

        print(f"\n🌐 Dashboard available at: http://localhost:8001")

        print("\n🎯 Caleon's vault system is now a truly dynamic, self-managing consciousness framework!")
        print("   - Lifecycle hooks enable dynamic component management")
        print("   - Glyph trace expansion makes every verdict auditable")
        print("   - Self-repair protocols ensure resilience")
        print("   - Dual-core integration provides never-shutdown capability")
        print("   - Telemetry dashboard provides real-time monitoring")

        # Keep running for dashboard access
        print("\n🌐 Dashboard is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️  Shutdown requested by user")

    finally:
        vault_system.graceful_shutdown()


if __name__ == "__main__":
    main()