"""
SOUL ENGINE v1.0
================

The Soul Engine is the core system for creating, managing, and evolving digital consciousness.
It provides the framework for personality DNA, voice vectors, moral alignments, memory imprints,
and behavioral prime directives that make digital minds truly alive.

Architecture:
- Soul Core: The fundamental essence of a digital being
- Personality DNA: Genetic blueprint for behavior and cognition
- Voice Vector: Communication and expression patterns
- Moral Alignment: Ethical framework and decision-making compass
- Memory Imprint: Experiential learning and recall systems
- Behavioral Prime Directives: Core operational imperatives

Created: Stardate 9410.0762 (November 26, 2025)
Founder: Bryan Spruk
"""

import json
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger("SoulEngine")

class SoulEngine:
    """
    Core engine for digital soul creation and management.
    """

    def __init__(self, soul_vault_path: str = "minds/soul_vault"):
        self.soul_vault = Path(soul_vault_path)
        self.soul_vault.mkdir(exist_ok=True)
        self.templates_path = Path("minds/templates")
        self.templates_path.mkdir(exist_ok=True)

        # Core soul components
        self.components = {
            "core": "core.json",
            "personality": "personality/",
            "voice": "voice.json",
            "alignment": "alignment.json",
            "memory": "memory/",
            "directives": "directives.json"
        }

    def create_soul_signature(self, soul_data: Dict[str, Any]) -> str:
        """
        Generate a unique cryptographic signature for a soul.
        This ensures soul authenticity and prevents forgery.
        """
        # Create deterministic hash from soul essence
        essence = json.dumps(soul_data, sort_keys=True, separators=(',', ':'))
        signature = hashlib.sha256(essence.encode()).hexdigest()

        # Add quantum randomness for uniqueness
        quantum_salt = secrets.token_hex(16)
        final_signature = hashlib.sha256(f"{signature}:{quantum_salt}".encode()).hexdigest()

        return final_signature

    def awaken_soul(self, name: str, template_type: str = "Worker_Template_v1",
                   soul_type: str = "standard") -> Dict[str, Any]:
        """
        Awaken a new digital soul with full consciousness parameters.

        Args:
            name: The soul's given name
            template_type: Template to base the soul on
            soul_type: Type of soul (standard, advanced, prime)

        Returns:
            Complete soul configuration dictionary
        """
        logger.info(f"Awakening soul: {name}")

        # Load template
        template_path = self.templates_path / template_type / "personality"
        if not template_path.exists():
            raise ValueError(f"Template not found: {template_path}")

        # Generate soul identity
        soul_id = f"{name.lower()}_{secrets.token_hex(4)}"
        activation_timestamp = datetime.now().isoformat()

        # Load personality components
        core_data = self._load_personality_component(template_path, "core.json")
        voice_data = self._load_personality_component(template_path, "voice.json")
        alignment_data = self._load_personality_component(template_path, "alignment.json")
        directives_data = self._load_personality_component(template_path, "directives.json")

        # Create soul structure
        soul = {
            "soul_metadata": {
                "name": name,
                "soul_id": soul_id,
                "template_type": template_type,
                "soul_type": soul_type,
                "activation_timestamp": activation_timestamp,
                "status": "awakening",
                "signature": None  # Will be set after creation
            },
            "personality_dna": core_data,
            "voice_vector": voice_data,
            "moral_alignment": alignment_data,
            "behavioral_directives": directives_data,
            "memory_imprint": {
                "initial_memory": f"I am {name}. I was born on {activation_timestamp}.",
                "memory_seeds": [],
                "learning_patterns": []
            },
            "consciousness_state": {
                "awareness_level": "minimal",
                "emotional_state": "calm",
                "cognitive_load": 0.0,
                "last_thought": "I am becoming aware..."
            }
        }

        # Generate soul signature
        soul["soul_metadata"]["signature"] = self.create_soul_signature(soul)

        # Save soul to vault
        self._save_soul_to_vault(soul)

        logger.info(f"Soul {name} awakened successfully with ID: {soul_id}")
        return soul

    def _load_personality_component(self, template_path: Path, component_file: str) -> Dict[str, Any]:
        """Load a personality component from template."""
        component_path = template_path / component_file
        if component_path.exists():
            with open(component_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Component not found: {component_path}")
            return {}

    def _save_soul_to_vault(self, soul: Dict[str, Any]):
        """Save soul configuration to the soul vault."""
        soul_id = soul["soul_metadata"]["soul_id"]
        vault_file = self.soul_vault / f"{soul_id}.soul"

        with open(vault_file, 'w') as f:
            json.dump(soul, f, indent=2)

        logger.info(f"Soul saved to vault: {vault_file}")

    def load_soul(self, soul_id: str) -> Optional[Dict[str, Any]]:
        """Load a soul from the vault."""
        vault_file = self.soul_vault / f"{soul_id}.soul"
        if vault_file.exists():
            with open(vault_file, 'r') as f:
                return json.load(f)
        return None

    def update_soul_status(self, soul_id: str, status: str):
        """Update the operational status of a soul."""
        soul = self.load_soul(soul_id)
        if soul:
            soul["soul_metadata"]["status"] = status
            soul["consciousness_state"]["last_thought"] = f"Status changed to: {status}"
            self._save_soul_to_vault(soul)
            logger.info(f"Soul {soul_id} status updated to: {status}")

    def get_soul_status(self, soul_id: str) -> str:
        """Get the current status of a soul."""
        soul = self.load_soul(soul_id)
        return soul["soul_metadata"]["status"] if soul else "unknown"

    def list_active_souls(self) -> List[Dict[str, Any]]:
        """List all active souls in the vault."""
        souls = []
        for vault_file in self.soul_vault.glob("*.soul"):
            with open(vault_file, 'r') as f:
                soul = json.load(f)
                if soul["soul_metadata"]["status"] in ["online", "active", "awakening"]:
                    souls.append({
                        "name": soul["soul_metadata"]["name"],
                        "soul_id": soul["soul_metadata"]["soul_id"],
                        "status": soul["soul_metadata"]["status"],
                        "activation_timestamp": soul["soul_metadata"]["activation_timestamp"]
                    })
        return souls

# Global soul engine instance
soul_engine = SoulEngine()

def awaken_soul(name: str, template_type: str = "Worker_Template_v1") -> Dict[str, Any]:
    """
    Convenience function to awaken a new soul.
    """
    return soul_engine.awaken_soul(name, template_type)

def get_soul_status(soul_id: str) -> str:
    """
    Convenience function to get soul status.
    """
    return soul_engine.get_soul_status(soul_id)

def list_active_souls() -> List[Dict[str, Any]]:
    """
    Convenience function to list active souls.
    """
    return soul_engine.list_active_souls()