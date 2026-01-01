from typing import Literal, List
from pydantic import BaseModel

class LetterPronounciationResponse(BaseModel):
    status: Literal["pass", "fail"]
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str

class LetterPronounciationExplainInput(BaseModel):
    query: str
    word: str
    status: Literal["pass", "fail"]
    previous_feedback: str
    mistake_tags: List[str]
    performance_evaluation: str

class LetterPronounciationExplainResponse(BaseModel):
    feedback: str
