from pydantic import BaseModel
from app.db.enums import ResourceType


class LetterPronounciationProblemResponse(BaseModel):
    id: int
    resource_type: ResourceType
    problem_count: int
    question: str
    letter: str
    letter_audio: str

