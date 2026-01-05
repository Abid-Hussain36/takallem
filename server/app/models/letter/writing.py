from typing import Literal, List, TypedDict
from fastapi import status
from pydantic import BaseModel


class WritingQAResponse(BaseModel):
    is_usable: bool
    confidence: float
    reasons: List[str]
    capture_tips: str

class WritingPhotoRetakeResponse(BaseModel):
    capture_tips: str

class LetterHandwritingScores(BaseModel):
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

class LetterJoiningScores(BaseModel):
    connection_accuracy: float
    positional_forms: float
    spacing_flow: float
    baseline_consistency: float
    dots_diacritics: float
    overall: float

class LetterJoiningResponse(BaseModel):
    status: Literal["pass", "fail"]
    confidence: float
    scores: LetterJoiningScores
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str
    