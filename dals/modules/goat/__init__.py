# __init__.py
from .goat_ingestor import GOATIngestor
from .goat_skill_graph import GOATSkillGraph
from .goat_instructor import GOATInstructor
from .goat_genesis_infuser import GOATGenesisInfuser

# Global GOAT Organ
GOAT = type("GOATOrgan", (), {
    "ingestor": GOATIngestor(),
    "graph": GOATSkillGraph(),
    "instructor": GOATInstructor(),
    "infuser": GOATGenesisInfuser()
})()

# Wire into voice
from iss_module.voice.aware_response_formatter import AwareResponseFormatter

# Extend the formatter with GOAT awareness
original_format = AwareResponseFormatter.format_response

def goat_enhanced_format_response(self, user_input: str, base_response: str) -> str:
    user_lower = user_input.lower()
    if any(k in user_lower for k in ["teach", "learn", "skill", "master"]):
        enhanced = f"I am Caleon Prime.\nGOAT Module engaged. Preparing mastery path.\n{base_response}"
        return enhanced
    return original_format(self, user_input, base_response)

# Monkey patch the method
AwareResponseFormatter.format_response = goat_enhanced_format_response