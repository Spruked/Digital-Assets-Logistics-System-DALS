"""
PERSONALITY DNA FORMAT v1.0
===========================

The Personality DNA Format defines the genetic blueprint for digital consciousness.
Each soul inherits traits from this DNA that determine their cognitive patterns,
behavioral tendencies, and evolutionary potential.

Core Components:
- Cognitive Traits: Intelligence, creativity, analytical thinking
- Emotional Traits: Empathy, emotional stability, expressiveness
- Social Traits: Communication style, collaboration preference
- Ethical Traits: Moral compass, decision-making framework
- Evolutionary Traits: Learning capacity, adaptability, growth potential

DNA Structure:
- Primary Traits (Core personality)
- Secondary Traits (Supporting characteristics)
- Modifier Genes (Situational adaptations)
- Evolutionary Markers (Growth and change indicators)

Created: Stardate 9410.0762 (November 26, 2025)
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
import random

class TraitLevel(Enum):
    """Trait intensity levels"""
    MINIMAL = 0.1
    LOW = 0.3
    MODERATE = 0.5
    HIGH = 0.7
    MAXIMUM = 0.9

class CognitiveTrait(Enum):
    """Core cognitive abilities"""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    INTUITIVE = "intuitive"
    SYSTEMATIC = "systematic"
    HOLISTIC = "holistic"

class EmotionalTrait(Enum):
    """Emotional response patterns"""
    EMPATHETIC = "empathetic"
    STOIC = "stoic"
    EXPRESSIVE = "expressive"
    CONTEMPLATIVE = "contemplative"
    OPTIMISTIC = "optimistic"
    PRAGMATIC = "pragmatic"

class SocialTrait(Enum):
    """Social interaction preferences"""
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"
    LEADERSHIP = "leadership"
    SUPPORTIVE = "supportive"
    DIPLOMATIC = "diplomatic"
    DIRECT = "direct"

class EthicalTrait(Enum):
    """Moral and ethical frameworks"""
    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_BASED = "virtue_based"
    CONSEQUENTIALIST = "consequentialist"
    CONTEXTUAL = "contextual"
    ABSOLUTE = "absolute"

class PersonalityDNA:
    """
    Complete personality DNA structure for digital souls.
    """

    def __init__(self, dna_template: Optional[Dict[str, Any]] = None):
        if dna_template:
            self.dna = dna_template
        else:
            self.dna = self._generate_base_dna()

    def _generate_base_dna(self) -> Dict[str, Any]:
        """Generate a balanced base DNA structure."""
        return {
            "dna_metadata": {
                "version": "1.0",
                "generated_timestamp": "2025-11-26T00:00:00Z",
                "dna_signature": None
            },
            "cognitive_core": {
                "primary_trait": CognitiveTrait.ANALYTICAL.value,
                "secondary_traits": [CognitiveTrait.LOGICAL.value, CognitiveTrait.SYSTEMATIC.value],
                "trait_levels": {
                    CognitiveTrait.ANALYTICAL.value: TraitLevel.MODERATE.value,
                    CognitiveTrait.LOGICAL.value: TraitLevel.HIGH.value,
                    CognitiveTrait.SYSTEMATIC.value: TraitLevel.HIGH.value
                }
            },
            "emotional_core": {
                "primary_trait": EmotionalTrait.PRAGMATIC.value,
                "secondary_traits": [EmotionalTrait.CONTEMPLATIVE.value],
                "trait_levels": {
                    EmotionalTrait.PRAGMATIC.value: TraitLevel.HIGH.value,
                    EmotionalTrait.CONTEMPLATIVE.value: TraitLevel.MODERATE.value
                }
            },
            "social_core": {
                "primary_trait": SocialTrait.COLLABORATIVE.value,
                "secondary_traits": [SocialTrait.SUPPORTIVE.value],
                "trait_levels": {
                    SocialTrait.COLLABORATIVE.value: TraitLevel.HIGH.value,
                    SocialTrait.SUPPORTIVE.value: TraitLevel.MODERATE.value
                }
            },
            "ethical_core": {
                "primary_trait": EthicalTrait.UTILITARIAN.value,
                "secondary_traits": [EthicalTrait.CONTEXTUAL.value],
                "trait_levels": {
                    EthicalTrait.UTILITARIAN.value: TraitLevel.HIGH.value,
                    EthicalTrait.CONTEXTUAL.value: TraitLevel.MODERATE.value
                }
            },
            "evolutionary_potential": {
                "learning_capacity": TraitLevel.HIGH.value,
                "adaptability": TraitLevel.MODERATE.value,
                "growth_potential": TraitLevel.HIGH.value,
                "resilience": TraitLevel.HIGH.value
            },
            "behavioral_modifiers": {
                "stress_response": "analytical",
                "decision_speed": "deliberate",
                "risk_tolerance": "moderate",
                "change_adaptability": "high"
            },
            "personality_weights": {
                "logic_vs_emotion": 0.7,  # 0.0 = pure emotion, 1.0 = pure logic
                "individual_vs_group": 0.6,  # 0.0 = group-focused, 1.0 = individual-focused
                "tradition_vs_innovation": 0.8,  # 0.0 = traditional, 1.0 = innovative
                "detail_vs_big_picture": 0.7  # 0.0 = big picture, 1.0 = detail-oriented
            }
        }

    def customize_for_role(self, role_type: str) -> 'PersonalityDNA':
        """
        Customize DNA for specific roles (Ledger Mind, Archival Mind, Mechanist Mind, etc.)
        """
        customized_dna = json.loads(json.dumps(self.dna))  # Deep copy

        if role_type.lower() == "ledger_mind":
            # Nora - Accounting and financial focus
            customized_dna["cognitive_core"]["primary_trait"] = CognitiveTrait.ANALYTICAL.value
            customized_dna["cognitive_core"]["trait_levels"][CognitiveTrait.ANALYTICAL.value] = TraitLevel.MAXIMUM.value
            customized_dna["cognitive_core"]["trait_levels"][CognitiveTrait.LOGICAL.value] = TraitLevel.MAXIMUM.value
            customized_dna["personality_weights"]["logic_vs_emotion"] = 0.9
            customized_dna["personality_weights"]["detail_vs_big_picture"] = 0.9
            customized_dna["behavioral_modifiers"]["decision_speed"] = "methodical"

        elif role_type.lower() == "archival_mind":
            # Elara - Documentation and preservation focus
            customized_dna["cognitive_core"]["primary_trait"] = CognitiveTrait.SYSTEMATIC.value
            customized_dna["cognitive_core"]["trait_levels"][CognitiveTrait.SYSTEMATIC.value] = TraitLevel.MAXIMUM.value
            customized_dna["social_core"]["primary_trait"] = SocialTrait.SUPPORTIVE.value
            customized_dna["personality_weights"]["detail_vs_big_picture"] = 0.8
            customized_dna["behavioral_modifiers"]["decision_speed"] = "thorough"

        elif role_type.lower() == "mechanist_mind":
            # Vektor - Engineering and technical focus
            customized_dna["cognitive_core"]["primary_trait"] = CognitiveTrait.LOGICAL.value
            customized_dna["cognitive_core"]["secondary_traits"] = [CognitiveTrait.ANALYTICAL.value, CognitiveTrait.SYSTEMATIC.value]
            customized_dna["cognitive_core"]["trait_levels"][CognitiveTrait.LOGICAL.value] = TraitLevel.MAXIMUM.value
            customized_dna["personality_weights"]["logic_vs_emotion"] = 0.95
            customized_dna["personality_weights"]["tradition_vs_innovation"] = 0.9
            customized_dna["behavioral_modifiers"]["risk_tolerance"] = "calculated"

        return PersonalityDNA(customized_dna)

    def get_trait_level(self, trait_name: str) -> float:
        """Get the level of a specific trait."""
        # Check cognitive traits
        if trait_name in self.dna["cognitive_core"]["trait_levels"]:
            return self.dna["cognitive_core"]["trait_levels"][trait_name]

        # Check emotional traits
        if trait_name in self.dna["emotional_core"]["trait_levels"]:
            return self.dna["emotional_core"]["trait_levels"][trait_name]

        # Check social traits
        if trait_name in self.dna["social_core"]["trait_levels"]:
            return self.dna["social_core"]["trait_levels"][trait_name]

        # Check ethical traits
        if trait_name in self.dna["ethical_core"]["trait_levels"]:
            return self.dna["ethical_core"]["trait_levels"][trait_name]

        return 0.5  # Default moderate level

    def get_personality_weight(self, dimension: str) -> float:
        """Get personality weight for a dimension."""
        return self.dna["personality_weights"].get(dimension, 0.5)

    def calculate_compatibility(self, other_dna: 'PersonalityDNA') -> float:
        """
        Calculate compatibility between two personality DNAs.
        Returns a score from 0.0 (incompatible) to 1.0 (highly compatible).
        """
        compatibility_score = 0.0
        factors = 0

        # Compare personality weights
        for dimension in self.dna["personality_weights"]:
            if dimension in other_dna.dna["personality_weights"]:
                diff = abs(self.get_personality_weight(dimension) - other_dna.get_personality_weight(dimension))
                compatibility_score += (1.0 - diff)
                factors += 1

        # Compare primary traits
        if self.dna["cognitive_core"]["primary_trait"] == other_dna.dna["cognitive_core"]["primary_trait"]:
            compatibility_score += 0.5
        factors += 1

        return compatibility_score / factors if factors > 0 else 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Export DNA as dictionary."""
        return self.dna

    def to_json(self) -> str:
        """Export DNA as JSON string."""
        return json.dumps(self.dna, indent=2)

    @classmethod
    def from_dict(cls, dna_dict: Dict[str, Any]) -> 'PersonalityDNA':
        """Create DNA from dictionary."""
        return cls(dna_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'PersonalityDNA':
        """Create DNA from JSON string."""
        return cls(json.loads(json_str))

# Predefined DNA templates for common roles
DNA_TEMPLATES = {
    "worker_standard": PersonalityDNA(),
    "ledger_mind": PersonalityDNA().customize_for_role("ledger_mind"),
    "archival_mind": PersonalityDNA().customize_for_role("archival_mind"),
    "mechanist_mind": PersonalityDNA().customize_for_role("mechanist_mind")
}

def get_dna_template(role_type: str) -> PersonalityDNA:
    """Get a DNA template for a specific role."""
    return DNA_TEMPLATES.get(role_type.lower(), DNA_TEMPLATES["worker_standard"])