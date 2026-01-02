from typing import Literal, List, TypedDict
from pydantic import BaseModel


class WritingQAResponse(BaseModel):
    is_usable: bool
    confidence: float
    reasons: List[str]
    capture_tips: str

class WritingPhotoRetakeResponse(BaseModel):
    capture_tips: str

class LetterHandwritingScores(TypedDict):
    legibility: float
    form_accuracy: float
    dots_diacritics: float
    baseline_proportion: float
    overall: float

class LetterWritingResponse(BaseModel):
    status: Literal["pass", "fail"]
    confidence: float
    scores: LetterHandwritingScores
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str