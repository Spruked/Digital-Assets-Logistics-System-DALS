# glyph_generator.py

"""
Glyph Generator - Dynamic Symbol Creation for Reasoning Traces

This module generates unique glyphs (symbols) that represent reasoning steps,
decisions, and philosophical concepts. Each glyph is a visual/mathematical
representation that can be traced through the reasoning process.
"""

import hashlib
import math
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class GlyphType(Enum):
    """Types of glyphs that can be generated"""
    CONCEPT = "concept"           # Represents abstract concepts
    DECISION = "decision"         # Represents decision points
    EVIDENCE = "evidence"         # Represents evidence/data
    REASONING = "reasoning"       # Represents reasoning steps
    PHILOSOPHICAL = "philosophical"  # Represents philosophical principles
    EMOTIONAL = "emotional"       # Represents emotional states
    INTUITIVE = "intuitive"       # Represents intuitive insights


class GlyphShape(Enum):
    """Geometric shapes for glyph visualization"""
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    HEXAGON = "hexagon"
    STAR = "star"
    SPIRAL = "spiral"
    WAVE = "wave"
    CROSS = "cross"


class GlyphGenerator:
    """
    Generates unique glyphs for reasoning trace visualization.

    Each glyph represents a specific concept, decision, or reasoning step
    with visual and mathematical properties that can be tracked through
    the reasoning process.
    """

    def __init__(self, seed: Optional[str] = None):
        """
        Initialize the glyph generator.

        Args:
            seed: Optional seed for reproducible glyph generation
        """
        self.seed = seed or str(time.time())
        self.random = random.Random(self.seed)

        # Glyph registry for uniqueness tracking
        self.generated_glyphs: Dict[str, Dict[str, Any]] = {}

        # Shape rotation for variety
        self.shape_cycle = list(GlyphShape)

        print("🎨 Glyph Generator initialized")

    def generate_glyph(self, content: str, glyph_type: GlyphType,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a unique glyph for given content.

        Args:
            content: Content to represent with glyph
            glyph_type: Type of glyph to generate
            metadata: Additional metadata for the glyph

        Returns:
            Glyph dictionary with visual and mathematical properties
        """
        # Create unique identifier
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp = datetime.now().isoformat()
        unique_id = f"{glyph_type.value}_{content_hash}_{int(time.time()*1000)}"

        # Generate glyph properties
        glyph = {
            "id": unique_id,
            "type": glyph_type.value,
            "content_hash": content_hash,
            "timestamp": timestamp,
            "shape": self._select_shape(content),
            "color": self._generate_color(content),
            "size": self._calculate_size(content),
            "rotation": self._calculate_rotation(content),
            "complexity": self._calculate_complexity(content),
            "mathematical_properties": self._generate_mathematical_properties(content),
            "visual_representation": self._generate_visual_representation(content),
            "metadata": metadata or {}
        }

        # Store for uniqueness tracking
        self.generated_glyphs[unique_id] = glyph

        return glyph

    def _select_shape(self, content: str) -> str:
        """Select appropriate shape based on content characteristics"""
        content_length = len(content)
        word_count = len(content.split())

        # Shape selection logic based on content properties
        if word_count > 20:
            return GlyphShape.SPIRAL.value
        elif "decision" in content.lower() or "choose" in content.lower():
            return GlyphShape.CROSS.value
        elif "evidence" in content.lower() or "data" in content.lower():
            return GlyphShape.SQUARE.value
        elif "emotion" in content.lower() or "feel" in content.lower():
            return GlyphShape.WAVE.value
        elif content_length > 100:
            return GlyphShape.HEXAGON.value
        elif "?" in content:
            return GlyphShape.TRIANGLE.value
        else:
            # Cycle through shapes for variety
            shape_index = hash(content) % len(self.shape_cycle)
            return self.shape_cycle[shape_index].value

    def _generate_color(self, content: str) -> Dict[str, float | str]:
        """Generate RGB color based on content hash"""
        hash_obj = hashlib.md5(content.encode())
        hash_bytes = hash_obj.digest()

        # Use hash bytes to generate RGB values
        r = hash_bytes[0] / 255.0
        g = hash_bytes[1] / 255.0
        b = hash_bytes[2] / 255.0

        # Ensure good contrast and visibility
        # Normalize to avoid too dark colors
        max_val = max(r, g, b)
        if max_val < 0.3:
            factor = 0.3 / max_val
            r *= factor
            g *= factor
            b *= factor

        return {
            "r": round(r, 3),
            "g": round(g, 3),
            "b": round(b, 3),
            "hex": f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        }

    def _calculate_size(self, content: str) -> float:
        """Calculate glyph size based on content significance"""
        base_size = 1.0
        content_length = len(content)
        word_count = len(content.split())

        # Size modifiers
        length_factor = min(content_length / 100.0, 2.0)  # Max 2x for very long content
        word_factor = min(word_count / 10.0, 1.5)        # Max 1.5x for many words

        # Importance indicators
        importance_boost = 0.0
        if any(word in content.lower() for word in ["critical", "important", "key", "essential"]):
            importance_boost = 0.3
        if "!" in content:
            importance_boost += 0.2

        return round(base_size * (1 + length_factor + word_factor + importance_boost), 2)

    def _calculate_rotation(self, content: str) -> float:
        """Calculate rotation angle based on content"""
        # Use content hash to determine rotation
        hash_val = int(hashlib.sha256(content.encode()).hexdigest()[:8], 16)
        rotation = (hash_val % 360)  # 0-359 degrees

        # Prefer certain angles for better visual appeal
        preferred_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        closest_angle = min(preferred_angles, key=lambda x: abs(x - rotation))
        return float(closest_angle)

    def _calculate_complexity(self, content: str) -> float:
        """Calculate visual complexity of the glyph"""
        base_complexity = 0.5
        factors = []

        # Length complexity
        factors.append(min(len(content) / 200.0, 1.0))

        # Word complexity
        words = content.split()
        factors.append(min(len(words) / 20.0, 1.0))

        # Punctuation complexity
        punctuation_count = sum(1 for char in content if char in "!?.:;")
        factors.append(min(punctuation_count / 5.0, 1.0))

        # Technical term complexity
        technical_terms = ["algorithm", "philosophy", "mathematical", "quantum", "neural"]
        technical_count = sum(1 for term in technical_terms if term in content.lower())
        factors.append(min(technical_count / 3.0, 1.0))

        complexity = base_complexity + sum(factors) / len(factors)
        return round(min(complexity, 1.0), 2)

    def _generate_mathematical_properties(self, content: str) -> Dict[str, Any]:
        """Generate mathematical properties for the glyph"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Convert hash to numerical values
        hash_int = int(content_hash[:16], 16)

        return {
            "prime_factors": self._get_prime_factors(hash_int),
            "fibonacci_relation": self._find_fibonacci_relation(hash_int),
            "golden_ratio_alignment": self._calculate_golden_ratio_alignment(content),
            "fractal_dimension": self._estimate_fractal_dimension(content),
            "entropy": self._calculate_entropy(content)
        }

    def _generate_visual_representation(self, content: str) -> Dict[str, Any]:
        """Generate visual representation data"""
        return {
            "svg_path": self._generate_svg_path(content),
            "ascii_art": self._generate_ascii_art(content),
            "coordinates": self._generate_coordinates(content),
            "pattern": self._generate_pattern(content)
        }

    def _get_prime_factors(self, n: int) -> List[int]:
        """Get prime factors of a number"""
        factors = []
        i = 2
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors

    def _find_fibonacci_relation(self, n: int) -> Dict[str, Any]:
        """Find relation to Fibonacci sequence"""
        fib_sequence = [0, 1]
        while fib_sequence[-1] < n:
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

        # Find closest Fibonacci numbers
        closest_lower = max([f for f in fib_sequence if f <= n], default=0)
        closest_higher = min([f for f in fib_sequence if f >= n], default=n)

        return {
            "closest_lower": closest_lower,
            "closest_higher": closest_higher,
            "distance_to_lower": n - closest_lower,
            "distance_to_higher": closest_higher - n
        }

    def _calculate_golden_ratio_alignment(self, content: str) -> float:
        """Calculate how well content aligns with golden ratio"""
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618

        content_length = len(content)
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        ratio = content_length / word_count
        alignment = 1.0 - abs(ratio - phi) / phi

        return round(max(0.0, alignment), 3)

    def _estimate_fractal_dimension(self, content: str) -> float:
        """Estimate fractal dimension of content structure"""
        # Simple estimation based on content complexity
        length = len(content)
        unique_chars = len(set(content))

        if length == 0:
            return 0.0

        # Rough fractal dimension estimation
        dimension = math.log(unique_chars) / math.log(length) if length > 1 else 0.0
        return round(min(dimension, 2.0), 3)

    def _calculate_entropy(self, content: str) -> float:
        """Calculate Shannon entropy of content"""
        if not content:
            return 0.0

        char_counts = {}
        for char in content:
            char_counts[char] = char_counts.get(char, 0) + 1

        entropy = 0.0
        length = len(content)
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return round(entropy, 3)

    def _generate_svg_path(self, content: str) -> str:
        """Generate SVG path data for glyph visualization"""
        # Simple SVG path generation based on content hash
        hash_val = int(hashlib.md5(content.encode()).hexdigest()[:8], 16)

        # Generate a simple geometric path
        if hash_val % 4 == 0:
            return "M 50 10 L 90 50 L 50 90 L 10 50 Z"  # Diamond
        elif hash_val % 4 == 1:
            return "M 50 10 Q 90 50 50 90 Q 10 50 50 10"  # Rounded diamond
        elif hash_val % 4 == 2:
            return "M 10 50 Q 50 10 90 50 Q 50 90 10 50"  # Horizontal oval
        else:
            return "M 50 10 L 80 40 L 50 70 L 20 40 Z"  # Triangle

    def _generate_ascii_art(self, content: str) -> str:
        """Generate ASCII art representation"""
        shapes = [
            "  /\\  \n /  \\ \n/____\\",
            " ____ \n|    |\n|____|",
            "  ()  \n /  \\ \n/____\\",
            "   *   \n  ***  \n ***** "
        ]

        hash_val = hash(content) % len(shapes)
        return shapes[hash_val]

    def _generate_coordinates(self, content: str) -> List[Tuple[float, float]]:
        """Generate coordinate points for glyph"""
        points = []
        hash_val = int(hashlib.md5(content.encode()).hexdigest()[:8], 16)

        # Generate 5-8 coordinate points based on hash
        num_points = 5 + (hash_val % 4)

        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            radius = 0.5 + (hash_val % 100) / 200.0
            x = 0.5 + radius * math.cos(angle)
            y = 0.5 + radius * math.sin(angle)
            points.append((round(x, 3), round(y, 3)))

        return points

    def _generate_pattern(self, content: str) -> Dict[str, Any]:
        """Generate pattern data for glyph"""
        hash_val = int(hashlib.md5(content.encode()).hexdigest()[:8], 16)

        return {
            "pattern_type": ["solid", "striped", "dotted", "gradient"][hash_val % 4],
            "density": (hash_val % 10) / 10.0,
            "symmetry": ["radial", "bilateral", "asymmetric"][hash_val % 3],
            "repetition": hash_val % 5 + 1
        }

    def get_glyph_by_id(self, glyph_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a glyph by its ID"""
        return self.generated_glyphs.get(glyph_id)

    def list_glyphs_by_type(self, glyph_type: GlyphType) -> List[Dict[str, Any]]:
        """List all glyphs of a specific type"""
        return [
            glyph for glyph in self.generated_glyphs.values()
            if glyph["type"] == glyph_type.value
        ]

    def get_glyph_stats(self) -> Dict[str, Any]:
        """Get statistics about generated glyphs"""
        types = {}
        total_glyphs = len(self.generated_glyphs)

        for glyph in self.generated_glyphs.values():
            glyph_type = glyph["type"]
            types[glyph_type] = types.get(glyph_type, 0) + 1

        return {
            "total_glyphs": total_glyphs,
            "types": types,
            "avg_complexity": sum(g["complexity"] for g in self.generated_glyphs.values()) / total_glyphs if total_glyphs > 0 else 0,
            "avg_size": sum(g["size"] for g in self.generated_glyphs.values()) / total_glyphs if total_glyphs > 0 else 0
        }

    def clear_glyphs(self):
        """Clear all generated glyphs"""
        self.generated_glyphs.clear()