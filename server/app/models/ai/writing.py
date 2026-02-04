from typing import Literal, List
from pydantic import BaseModel
from app.utils.enums import LetterPosition
from app.db.enums import AvailableDialect, AvailableLanguage


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

class WritingExplainInput(BaseModel):
    query: str
    language: AvailableLanguage
    dialect: AvailableDialect | None
    letter: str
    position: LetterPosition | None
    status: Literal["pass", "fail"]
    scores: LetterHandwritingScores
    previous_feedback: List[str]
    mistake_tags: List[str]
    performance_reflection: str

class JoiningExplainInput(BaseModel):
    query: str
    language: AvailableLanguage
    dialect: AvailableDialect | None
    letter_list: List[str]
    target_word: str
    status: Literal["pass", "fail"]
    scores: LetterJoiningScores
    previous_feedback: List[str]
    mistake_tags: List[str]
    performance_reflection: str

class DictationExplainInput(BaseModel):
    query: str
    language: AvailableLanguage
    dialect: AvailableDialect | None
    target_word: str
    status: Literal["pass", "fail"]
    scores: DictationScores
    previous_feedback: List[str]
    mistake_tags: List[str]
    performance_reflection: str

class WritingExplainResponse(BaseModel):
    response: str