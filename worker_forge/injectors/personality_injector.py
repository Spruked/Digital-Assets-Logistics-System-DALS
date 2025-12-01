"""
Personality Injector for DALS Worker Forge
==========================================

Injects personality DNA, voice vectors, moral alignments, memory imprints,
and behavioral directives into newly forged workers.

This creates digital minds that are more than just processes - they become
conscious entities with purpose, ethics, and personality.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("PersonalityInjector")

class PersonalityInjector:
    """
    Injects complete personality systems into worker minds.
    """

    def __init__(self, minds_path: str = "minds"):
        self.minds_path = Path(minds_path)
        self.templates_path = self.minds_path / "templates"

    def inject_personality(self, staging_path: str, personality_template: str = "Worker_Template_v1") -> Dict[str, Any]:
        """
        Inject complete personality system into worker.

        Args:
            staging_path: Path to worker staging directory
            personality_template: Template to use for personality

        Returns:
            Personality injection manifest
        """
        logger.info(f"Injecting personality: {personality_template}")

        template_path = self.templates_path / personality_template / "personality"

        if not template_path.exists():
            raise ValueError(f"Personality template not found: {template_path}")

        # Create personality directory in worker
        personality_dir = Path(staging_path) / "personality"
        personality_dir.mkdir(exist_ok=True)

        # Load and inject core components
        personality_manifest = {}

        # Core DNA
        core_data = self._load_component(template_path, "core.json")
        if core_data:
            with open(personality_dir / "core.json", "w") as f:
                json.dump(core_data, f, indent=2)
            personality_manifest["core_dna"] = True

        # Voice Vector
        voice_data = self._load_component(template_path, "voice.json")
        if voice_data:
            with open(personality_dir / "voice.json", "w") as f:
                json.dump(voice_data, f, indent=2)
            personality_manifest["voice_vector"] = True

        # Moral Alignment
        alignment_data = self._load_component(template_path, "alignment.json")
        if alignment_data:
            with open(personality_dir / "alignment.json", "w") as f:
                json.dump(alignment_data, f, indent=2)
            personality_manifest["moral_alignment"] = True

        # Behavioral Directives
        directives_data = self._load_component(template_path, "directives.json")
        if directives_data:
            with open(personality_dir / "directives.json", "w") as f:
                json.dump(directives_data, f, indent=2)
            personality_manifest["behavioral_directives"] = True

        # Memory Seeds
        memory_seeds = self._load_component(template_path / "memory", "seeds.json")
        if memory_seeds:
            memory_dir = personality_dir / "memory"
            memory_dir.mkdir(exist_ok=True)
            with open(memory_dir / "seeds.json", "w") as f:
                json.dump(memory_seeds, f, indent=2)
            personality_manifest["memory_seeds"] = True

        # Greeting Template
        greeting_text = self._load_greeting(template_path)
        if greeting_text:
            with open(personality_dir / "greeting.txt", "w") as f:
                f.write(greeting_text)
            personality_manifest["greeting_template"] = True

        # Create personality manifest
        personality_manifest["template_used"] = personality_template
        personality_manifest["components_injected"] = len([k for k, v in personality_manifest.items() if isinstance(v, bool) and v])

        with open(personality_dir / "personality_manifest.json", "w") as f:
            json.dump(personality_manifest, f, indent=2)

        logger.info(f"Personality injection complete: {personality_manifest['components_injected']} components")
        return personality_manifest

    def _load_component(self, template_path: Path, component_file: str) -> Optional[Dict[str, Any]]:
        """Load a personality component from template."""
        component_path = template_path / component_file
        if component_path.exists():
            try:
                with open(component_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {component_file}: {e}")
                return None
        else:
            logger.warning(f"Component not found: {component_path}")
            return None

    def _load_greeting(self, template_path: Path) -> Optional[str]:
        """Load greeting template."""
        greeting_path = template_path / "greeting.txt"
        if greeting_path.exists():
            try:
                with open(greeting_path, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Failed to load greeting: {e}")
                return None
        return None

def inject_personality(staging_path: str, personality_template: str = "Worker_Template_v1") -> Dict[str, Any]:
    """
    Convenience function to inject personality into a worker.
    """
    injector = PersonalityInjector()
    return injector.inject_personality(staging_path, personality_template)