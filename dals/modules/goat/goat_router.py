# goat_router.py
from fastapi import APIRouter
from .goat_instructor import GOATInstructor

router = APIRouter(prefix="/goat", tags=["GOAT"])

instructor = GOATInstructor()

@router.post("/teach")
async def teach_skill(request: dict):
    path = request["skill_path"]
    lesson = instructor.generate_lesson(path)
    return {"lesson": lesson.dict()}

@router.get("/path/{start}/{goal}")
async def get_path(start: str, goal: str):
    return {"path": instructor.graph.get_learning_path(start, goal)}