# knowledge/interview_engine.py
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

class KnowledgeInterviewEngine:
    """
    AI Interview Engine for Knowledge Immortality
    Phase 11-A2: Knowledge Preservation Pipeline
    """

    def __init__(self):
        self.profiles = self.load_profiles()
        self.session = {}
        self.session_id = None

    def load_profiles(self) -> Dict[str, Any]:
        """Load profession-specific interview templates"""
        return {
            "mechanic": {
                "Ford": [
                    "List the model lines you specialize in (F-Series, Mustang, Transit…)",
                    "What systems are you certified in (powertrain, hybrid, transmission…)",
                    "How many years in the field?",
                    "List the top 10 repairs you can diagnose blindfolded.",
                    "Describe 3 advanced diagnostic routines only experienced techs know.",
                    "What proprietary Ford procedures do you use regularly?",
                    "What does a rookie mechanic ALWAYS get wrong?",
                    "What would you teach your younger self?"
                ],
                "General": [
                    "What vehicle makes/models are you most experienced with?",
                    "What automotive systems do you master (engine, transmission, electrical…)?",
                    "How many years as a certified mechanic?",
                    "Describe your most complex repair from start to finish.",
                    "What diagnostic tools do you swear by?",
                    "What's the hardest automotive problem you've solved?",
                    "What would you teach every new mechanic on day one?"
                ]
            },
            "cnc_machinist": [
                "What machines do you master (Haas, DMG, Mazak…)?",
                "What tolerances do you consistently achieve (±0.0001 in, etc.)?",
                "List 5 complex parts you've programmed from scratch.",
                "What G-code tricks do you use that others miss?",
                "How do you compensate for thermal drift?",
                "What would break a rookie on day one?",
                "Describe your most challenging machining project.",
                "What CAD/CAM software do you prefer and why?"
            ],
            "nurse": [
                "What certifications do you hold (ACLS, PALS, TNCC…)?",
                "Describe your triage decision ladder in chaos.",
                "What's the hardest call you ever made under pressure?",
                "How do you spot subtle decline before alarms?",
                "What protocol do you follow that saves lives quietly?",
                "How many years in critical care?",
                "What's your specialty area (ER, ICU, OR…)?",
                "What would you teach new nurses about patient assessment?"
            ],
            "software_engineer": [
                "What is your name and current role?",
                "Primary stack (e.g., React + Node + PostgreSQL)?",
                "Biggest system you scaled (users, QPS, data)?",
                "Design pattern you swear by?",
                "Worst production fire you fixed?",
                "One principle you'd drill into every junior dev?",
                "What languages/frameworks do you master?",
                "How many years coding professionally?",
                "What's your most complex system architecture?"
            ],
            "chef": [
                "What cuisine specialties do you master?",
                "How many years in professional kitchens?",
                "What's your signature dish and technique?",
                "How do you manage a busy service rush?",
                "What knife skills are essential for any cook?",
                "Describe your most challenging menu creation.",
                "What would you teach culinary students first?"
            ],
            "electrician": [
                "What electrical systems do you specialize in (residential, commercial, industrial…)?",
                "What codes and standards do you follow (NEC, local…)?",
                "How many years licensed?",
                "Describe your most complex electrical project.",
                "What safety protocols do you always follow?",
                "What would trip up a new electrician?",
                "What diagnostic tools are in your kit?"
            ],
            "plumber": [
                "What plumbing systems do you master (residential, commercial, industrial…)?",
                "What codes do you work under?",
                "How many years licensed?",
                "Describe your most challenging pipe repair.",
                "What tools are essential for any plumber?",
                "What would you teach apprentice plumbers first?",
                "How do you handle emergency calls?"
            ],
            "welder": [
                "What welding processes do you master (MIG, TIG, Stick…)?",
                "What materials do you work with most?",
                "How many years welding professionally?",
                "What certifications do you hold?",
                "Describe your most precise weld.",
                "What safety gear is non-negotiable?",
                "What would you teach welding apprentices?"
            ],
            "carpenter": [
                "What carpentry specialties do you have (framing, finish, cabinetry…)?",
                "What tools are in your essential kit?",
                "How many years building professionally?",
                "Describe your most complex project.",
                "What woodworking techniques do you master?",
                "What would break a rookie carpenter?",
                "How do you ensure precision in measurements?"
            ]
        }

    def start_session(self, profession: str, specialization: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new interview session
        Returns session info and first question set
        """
        self.session_id = f"knowledge_{int(datetime.utcnow().timestamp())}"

        # Find appropriate question set
        questions = []
        if profession in self.profiles:
            if specialization and specialization in self.profiles[profession]:
                questions = self.profiles[profession][specialization]
            elif isinstance(self.profiles[profession], list):
                questions = self.profiles[profession]
            else:
                # Use general mechanic questions as fallback
                questions = self.profiles["mechanic"]["General"]

        # Fallback to generic questions if no specific profile found
        if not questions:
            questions = [
                "What is your profession and specialization?",
                "How many years of experience do you have?",
                "What are your top 3 areas of mastery?",
                "Describe a complex problem you solved.",
                "What advice would you give your younger self?",
                "What tools or techniques are essential in your field?",
                "What's the most challenging project you've completed?",
                "What would you teach someone new to your profession?"
            ]

        self.session = {
            "session_id": self.session_id,
            "profession": profession,
            "specialization": specialization,
            "questions": questions,
            "answers": [],
            "started_at": datetime.utcnow().isoformat() + "Z",
            "status": "active"
        }

        return {
            "session_id": self.session_id,
            "question_count": len(questions),
            "questions": questions,
            "estimated_time": f"{len(questions) * 3} minutes"
        }

    def submit_answer(self, question_index: int, answer: str) -> Dict[str, Any]:
        """Submit answer for a specific question"""
        if not self.session or self.session.get("status") != "active":
            raise ValueError("No active interview session")

        if question_index < 0 or question_index >= len(self.session["questions"]):
            raise ValueError("Invalid question index")

        question = self.session["questions"][question_index]

        # Check if answer already exists for this question
        existing_answer = None
        for i, ans in enumerate(self.session["answers"]):
            if ans["question_index"] == question_index:
                existing_answer = i
                break

        answer_data = {
            "question_index": question_index,
            "question": question,
            "answer": answer.strip(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "word_count": len(answer.split())
        }

        if existing_answer is not None:
            self.session["answers"][existing_answer] = answer_data
        else:
            self.session["answers"].append(answer_data)

        # Check if interview is complete
        if len(self.session["answers"]) >= len(self.session["questions"]):
            self.session["status"] = "completed"
            self.session["completed_at"] = datetime.utcnow().isoformat() + "Z"

        return {
            "question_index": question_index,
            "accepted": True,
            "remaining_questions": len(self.session["questions"]) - len(self.session["answers"]),
            "session_complete": self.session["status"] == "completed"
        }

    def get_progress(self) -> Dict[str, Any]:
        """Get current interview progress"""
        if not self.session:
            return {"status": "no_session"}

        total_questions = len(self.session["questions"])
        answered_questions = len(self.session["answers"])

        return {
            "session_id": self.session["session_id"],
            "status": self.session["status"],
            "progress": f"{answered_questions}/{total_questions}",
            "percentage": round((answered_questions / total_questions) * 100, 1) if total_questions > 0 else 0,
            "remaining": total_questions - answered_questions,
            "started_at": self.session["started_at"],
            "completed_at": self.session.get("completed_at")
        }

    def get_raw_data(self) -> Dict[str, Any]:
        """Get complete session data for processing"""
        if not self.session:
            raise ValueError("No active session")

        return self.session.copy()

    def save_session(self, filepath: Optional[str] = None) -> str:
        """Save current session to file"""
        if not self.session:
            raise ValueError("No active session to save")

        if not filepath:
            os.makedirs("knowledge/sessions", exist_ok=True)
            filepath = f"knowledge/sessions/{self.session_id}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session, f, indent=2, ensure_ascii=False)

        return filepath

    def load_session(self, session_id: str) -> bool:
        """Load a saved session"""
        filepath = f"knowledge/sessions/{session_id}.json"
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'r', encoding='utf-8') as f:
            self.session = json.load(f)

        self.session_id = session_id
        return True

    def reset_session(self):
        """Reset the current session"""
        self.session = {}
        self.session_id = None