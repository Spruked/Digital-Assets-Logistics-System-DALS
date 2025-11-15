# goat_instructor.py
from .goat_models import Lesson, LessonStep, QuizQuestion
from .goat_skill_graph import GOATSkillGraph
from typing import List
import uuid

class GOATInstructor:
    def __init__(self):
        self.graph = GOATSkillGraph()

    def generate_lesson(self, skill_path: List[str], user_level: str = "novice") -> Lesson:
        steps = []
        for i, skill_id in enumerate(skill_path):
            node = self.graph.G.nodes[skill_id]
            steps.append(LessonStep(
                step=i+1,
                title=node["name"],
                objective=f"Master {node['name']}",
                instructions=self._expand_procedure(node),
                drill=f"Practice {node['name']} 5 times under supervision",
                voice_hint=f"Now focusing on {node['name']}. Pay attention to {node['common_mistakes'][0] if len(node['common_mistakes']) > 0 else 'details'}.",
                duration_min=7,
                safety=node["safety_warnings"][0] if node["safety_warnings"] else None
            ))

        return Lesson(
            id=str(uuid.uuid4())[:8],
            title=" → ".join([self.graph.G.nodes[s].get("name", s) for s in skill_path]),
            path=skill_path,
            steps=steps,
            quiz=self._generate_quiz(skill_path[-1]),
            voice_narrative=self._compile_narrative(steps),
            estimated_time=len(steps) * 7
        )

    def _generate_quiz(self, skill_id: str) -> List[QuizQuestion]:
        node = self.graph.G.nodes[skill_id]
        return [
            QuizQuestion(
                q=f"What is the first step in {node['name']}?",
                options=["A", "B", "C", "D"],
                correct=0,
                explanation="Always begin with safety check."
            )
        ]

    def _compile_narrative(self, steps: List[LessonStep]) -> str:
        return "Welcome to your training. We begin with safety. " + ". ".join([s.voice_hint for s in steps])