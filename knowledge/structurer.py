# knowledge/structurer.py
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class KnowledgeStructurer:
    """
    Knowledge Structuring Engine
    Converts raw interview data into structured NFT payload
    Phase 11-A2: Knowledge Preservation Pipeline
    """

    def __init__(self):
        self.experience_patterns = [
            r'(\d+)\s*years?\s*(?:of\s*)?(?:experience)?',
            r'(\d+)\s*yrs?',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]

    @staticmethod
    def extract_years(text: str) -> int:
        """Extract years of experience from text"""
        if isinstance(text, (int, float)):
            return int(text)

        text = str(text).lower()

        # Look for explicit year mentions
        for pattern in [
            r'(\d+)\s*years?\s*(?:of\s*)?(?:experience)?',
            r'(\d+)\s*yrs?',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?'
        ]:
            match = re.search(pattern, text)
            if match:
                years = int(match.group(1))
                # Handle "over X years" by adding 1
                if 'over' in text or 'more than' in text:
                    years += 1
                return years

        # Look for ranges like "5-10 years" and take the higher number
        range_match = re.search(r'(\d+)\s*-\s*(\d+)\s*years?', text)
        if range_match:
            return int(range_match.group(2))

        return 0

    @staticmethod
    def extract_list(text: str, separators: List[str] = None) -> List[str]:
        """Extract list items from text using various separators"""
        if not text or not isinstance(text, str):
            return []

        if separators is None:
            separators = [r'\n', r'\r', r'•', r'-', r'\d+\.', r';', r',']

        items = []
        working_text = text.strip()

        # Try each separator
        for sep in separators:
            if re.search(sep, working_text):
                parts = re.split(sep, working_text)
                for part in parts:
                    part = part.strip()
                    # Clean up common prefixes
                    part = re.sub(r'^\d+\.?\s*', '', part)
                    part = re.sub(r'^[-•*]\s*', '', part)

                    if len(part) > 3 and not part.lower().startswith(('and ', 'or ', 'but ')):
                        items.append(part)

                if items:
                    break

        # If no separators found, treat as single item
        if not items and len(working_text) > 3:
            items = [working_text]

        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            item_lower = item.lower().strip()
            if item_lower not in seen and len(item_lower) > 2:
                seen.add(item_lower)
                unique_items.append(item.strip())

        return unique_items[:10]  # Limit to 10 items

    @staticmethod
    def categorize_answer(question: str, answer: str) -> Dict[str, Any]:
        """Categorize an answer based on the question"""
        q_lower = question.lower()
        categorization = {
            "category": "general",
            "confidence": 0.5,
            "extracted_items": [],
            "metadata": {}
        }

        # Experience detection
        if any(word in q_lower for word in ['years', 'experience', 'time', 'how long']):
            years = KnowledgeStructurer.extract_years(answer)
            if years > 0:
                categorization.update({
                    "category": "experience",
                    "confidence": 0.9,
                    "extracted_items": [years],
                    "metadata": {"years_experience": years}
                })

        # Specialties/Skills detection
        elif any(word in q_lower for word in ['specialize', 'certified', 'master', 'expert', 'skilled', 'primary', 'main', 'specialties', 'skills', 'expertise']):
            items = KnowledgeStructurer.extract_list(answer)
            if items:
                categorization.update({
                    "category": "specialties",
                    "confidence": 0.8,
                    "extracted_items": items
                })

        # Procedures/Routines detection
        elif any(word in q_lower for word in ['procedure', 'routine', 'diagnose', 'repair', 'fix', 'process', 'technique']):
            items = KnowledgeStructurer.extract_list(answer)
            if items:
                categorization.update({
                    "category": "procedures",
                    "confidence": 0.8,
                    "extracted_items": items
                })

        # Teaching/Lessons detection
        elif any(word in q_lower for word in ['teach', 'rookie', 'advice', 'lesson', 'younger', 'new', 'beginner']):
            items = KnowledgeStructurer.extract_list(answer)
            if items:
                categorization.update({
                    "category": "teaching",
                    "confidence": 0.8,
                    "extracted_items": items
                })

        # Tools/Equipment detection
        elif any(word in q_lower for word in ['tool', 'equipment', 'software', 'kit', 'gear']):
            items = KnowledgeStructurer.extract_list(answer)
            if items:
                categorization.update({
                    "category": "tools",
                    "confidence": 0.8,
                    "extracted_items": items
                })

        # Challenges/Projects detection
        elif any(word in q_lower for word in ['challenge', 'project', 'complex', 'difficult', 'hardest', 'worst']):
            items = KnowledgeStructurer.extract_list(answer)
            if items:
                categorization.update({
                    "category": "challenges",
                    "confidence": 0.7,
                    "extracted_items": items
                })

        return categorization

    def build_nft_payload(self, raw_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build structured NFT payload from raw interview session
        """
        logger.info(f"Structuring knowledge for session {raw_session.get('session_id', 'unknown')}")

        # Handle both interview engine format and raw answers list
        answers = raw_session.get("answers", [])
        if answers and isinstance(answers[0], str):
            # Raw answers list (for testing) - convert to expected format
            questions = raw_session.get("questions", [])
            answers = [
                {
                    "question": questions[i] if i < len(questions) else f"Question {i+1}",
                    "answer": answer
                }
                for i, answer in enumerate(answers)
            ]

        # Initialize payload structure
        payload = {
            "name": "",  # Extract from first answer
            "expertise_level": "",
            "years_experience": 0,
            "profession": raw_session.get("profession", "Unknown"),
            "specialization": raw_session.get("specialization"),
            "specialties": [],
            "procedures_mastered": [],
            "signature_routines": [],
            "teaching_notes": [],
            "tools_mastered": [],
            "challenges_overcome": [],
            "key_insights": [],
            "founder_message": "Digitally preserved by Alpha CertSig. Knowledge immortality achieved.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "processing_metadata": {
                "session_id": raw_session.get("session_id"),
                "questions_answered": len(answers),
                "processing_engine": "KnowledgeStructurer v1.0"
            }
        }

        # Extract name from first answer (typically "What is your name?")
        if answers:
            first_answer = answers[0].get("answer", "").strip()
            if first_answer:
                payload["name"] = first_answer

        # Build expertise level
        profession = payload["profession"].replace("_", " ").title()
        specialization = payload.get("specialization")
        if specialization:
            payload["expertise_level"] = f"{specialization} {profession}"
        else:
            payload["expertise_level"] = profession

        # Process each answer
        categorized_data = {
            "experience": [],
            "specialties": [],
            "procedures": [],
            "teaching": [],
            "tools": [],
            "challenges": []
        }

        for answer_data in answers:
            question = answer_data.get("question", "")
            answer = answer_data.get("answer", "")

            if not answer.strip():
                continue

            # Categorize the answer
            categorization = self.categorize_answer(question, answer)

            # Add to appropriate category
            category = categorization["category"]
            if category in categorized_data:
                categorized_data[category].extend(categorization["extracted_items"])

                # Handle special case for experience
                if category == "experience" and categorization["metadata"].get("years_experience"):
                    payload["years_experience"] = max(
                        payload["years_experience"],
                        categorization["metadata"]["years_experience"]
                    )

        # Populate payload fields
        payload["specialties"] = list(set(categorized_data["specialties"]))  # Remove duplicates
        payload["procedures_mastered"] = list(set(categorized_data["procedures"]))
        payload["signature_routines"] = payload["procedures_mastered"][:5]  # Top 5
        payload["teaching_notes"] = list(set(categorized_data["teaching"]))
        payload["tools_mastered"] = list(set(categorized_data["tools"]))
        payload["challenges_overcome"] = list(set(categorized_data["challenges"]))

        # Generate key insights (combine teaching notes and challenges)
        payload["key_insights"] = payload["teaching_notes"][:3] + payload["challenges_overcome"][:2]

        # Add processing statistics
        payload["processing_metadata"].update({
            "total_specialties": len(payload["specialties"]),
            "total_procedures": len(payload["procedures_mastered"]),
            "total_teaching_points": len(payload["teaching_notes"]),
            "structured_at": datetime.utcnow().isoformat() + "Z"
        })

        logger.info(f"Knowledge structured: {len(payload['specialties'])} specialties, "
                   f"{len(payload['procedures_mastered'])} procedures, "
                   f"{payload['years_experience']} years experience")

        return payload

    def validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate structured payload for NFT minting readiness"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0
        }

        # Required fields
        required_fields = ["expertise_level", "profession", "timestamp"]
        for field in required_fields:
            if not payload.get(field):
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        # Experience validation
        if payload.get("years_experience", 0) <= 0:
            validation["warnings"].append("No years of experience detected")

        # Content validation
        total_content_items = (
            len(payload.get("specialties", [])) +
            len(payload.get("procedures_mastered", [])) +
            len(payload.get("teaching_notes", []))
        )

        if total_content_items < 3:
            validation["warnings"].append("Limited knowledge content detected")
            validation["score"] = 1
        elif total_content_items < 10:
            validation["score"] = 2
        else:
            validation["score"] = 3

        # Quality checks
        if len(payload.get("teaching_notes", [])) == 0:
            validation["warnings"].append("No teaching insights captured")

        if len(payload.get("challenges_overcome", [])) == 0:
            validation["warnings"].append("No challenge experiences captured")

        return validation

    def enhance_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance payload with additional metadata and insights"""
        enhanced = payload.copy()

        # Add expertise tier based on experience
        years = payload.get("years_experience", 0)
        if years >= 20:
            enhanced["expertise_tier"] = "Master"
        elif years >= 10:
            enhanced["expertise_tier"] = "Expert"
        elif years >= 5:
            enhanced["expertise_tier"] = "Advanced"
        elif years >= 2:
            enhanced["expertise_tier"] = "Intermediate"
        else:
            enhanced["expertise_tier"] = "Apprentice"

        # Add knowledge density score
        content_density = (
            len(payload.get("specialties", [])) * 2 +
            len(payload.get("procedures_mastered", [])) * 3 +
            len(payload.get("teaching_notes", [])) * 2 +
            len(payload.get("challenges_overcome", [])) * 2
        )
        enhanced["knowledge_density_score"] = min(content_density, 100)

        # Add profession insights
        profession_insights = self._generate_profession_insights(payload)
        enhanced["profession_insights"] = profession_insights

        return enhanced

    def _generate_profession_insights(self, payload: Dict[str, Any]) -> List[str]:
        """Generate profession-specific insights"""
        profession = payload.get("profession", "").lower()
        insights = []

        # Common insights for all professions
        if payload.get("years_experience", 0) > 10:
            insights.append("Decade+ of practical experience in the field")

        if len(payload.get("teaching_notes", [])) > 0:
            insights.append("Strong mentoring and knowledge transfer capabilities")

        # Profession-specific insights
        if profession == "mechanic":
            if len(payload.get("procedures_mastered", [])) > 5:
                insights.append("Extensive diagnostic and repair expertise")
            if any("ford" in spec.lower() for spec in payload.get("specialties", [])):
                insights.append("Ford-certified specialist knowledge")

        elif profession in ["software_engineer", "developer"]:
            if len(payload.get("tools_mastered", [])) > 3:
                insights.append("Multi-stack development proficiency")
            if payload.get("years_experience", 0) > 5:
                insights.append("Production system architecture experience")

        elif profession == "nurse":
            if len(payload.get("procedures_mastered", [])) > 3:
                insights.append("Critical care and emergency response expertise")
            if payload.get("years_experience", 0) > 5:
                insights.append("Advanced patient assessment and triage skills")

        return insights[:5]  # Limit to 5 insights