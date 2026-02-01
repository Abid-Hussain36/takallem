from pydantic import BaseModel
from typing import List, Literal
from app.models.db.vocab.vocab_word_response import VocabWordResponse
from app.db.enums import AvailableDialect, AvailableLanguage


class PronounciationScores(BaseModel):
    """The pronounciation scores for the user response with Azure STT"""
    accuracy: float = 0.0
    completeness: float = 0.0
    overall: float = 0.0


class SemanticEvaluation(BaseModel):
    """Shows how much the answer made sematic sense of for the question asked"""
    vocab_words_used: List[str] = []
    answer_makes_sense: bool = False
    grammar_notes: str = ""


class VoiceTutorInput(BaseModel):
    """Audio input of user's response"""
    question: str = ""
    language: AvailableLanguage = AvailableLanguage.FRENCH
    dialect: AvailableDialect | None = None
    vocab_words: List[VocabWordResponse] = []
    user_audio_base64: str = ""


class VoiceTutorOutput(BaseModel):
    """AI's evaluation of user's performance and feedback"""
    status: Literal["pass", "fail"]
    feedback_text: str = ""
    feedback_audio: str | None = None


class VoiceTutorState(BaseModel):
    # Input
    question: str = ""
    language: AvailableLanguage = AvailableLanguage.FRENCH
    dialect: AvailableDialect | None = None
    vocab_words: List[VocabWordResponse] = []
    user_audio_base64: str = ""
    # Evaluation
    transcription: str = ""
    pronounciation_scores: PronounciationScores = PronounciationScores()
    semantic_evaluation: SemanticEvaluation = SemanticEvaluation()
    # Output
    status: Literal["pass", "fail", "pending"] = "pending"
    feedback_text: str = ""
    feedback_audio: str | None = None
    # Error
    error: str | None = None


class VoiceTutorQuestionInput(BaseModel):
    question: str


class VoiceTutorQuestionOutput(BaseModel):
    question_audio: str