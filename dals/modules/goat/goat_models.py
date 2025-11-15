# goat_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class MasteryLevel(str, Enum):
    NOVICE = "novice"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    MASTER = "master"

class SkillNode(BaseModel):
    id: str = Field(..., description="Unique skill identifier")
    name: str
    description: str
    level: MasteryLevel
    prereqs: List[str] = Field(default_factory=list)
    tools_required: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    safety_warnings: List[str] = Field(default_factory=list)
    expert_sources: List[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LessonStep(BaseModel):
    step: int
    title: str
    objective: str
    instructions: str
    drill: str
    voice_hint: str
    duration_min: int
    safety: Optional[str] = None

class QuizQuestion(BaseModel):
    q: str
    options: List[str]
    correct: int
    explanation: str

class Lesson(BaseModel):
    id: str
    title: str
    path: List[str]
    steps: List[LessonStep]
    quiz: List[QuizQuestion]
    voice_narrative: str
    estimated_time: int

class ExpertProfile(BaseModel):
    expert_id: str
    name: str
    profession: str
    years_experience: int
    specialties: List[str]
    wisdom: List[str]
    genesis: bool = False