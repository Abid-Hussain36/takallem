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
    scores: LetterJoiningScores
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str

class DictationScores(BaseModel):
    word_accuracy: float
    letter_identity: float
    joining_quality: float
    legibility: float
    dots_diacritics: float
    baseline_spacing: float
    overall: float

class DictationResponse(BaseModel):
    status: Literal["pass", "fail"]
    detected_word: str
    scores: DictationScores
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str
    