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
    grammatical_score: float = 0.0
    grammar_notes: str = ""


class VoiceTutorInput(BaseModel):
    """Audio input of user's response"""
    question: str = ""
    language: AvailableLanguage = AvailableLanguage.FRENCH
    dialect: AvailableDialect | None = None
    vocab_words: List[VocabWordResponse] = []
    user_audio_base64: str | None = None


class VoiceTutorOutput(BaseModel):
    """AI's evaluation of user's performance and feedback"""
    transcription: str = ""
    pronounciation_scores: PronounciationScores = PronounciationScores()
    semantic_evaluation: SemanticEvaluation = SemanticEvaluation()
    status: Literal["pass", "fail"]
    performance_reflection: str
    feedback_text: str | None = None
    feedback_audio_base64: str | None = None


class VoiceTutorState(BaseModel):
    # Input
    question: str = ""
    language: AvailableLanguage = AvailableLanguage.FRENCH
    dialect: AvailableDialect | None = None
    vocab_words: List[VocabWordResponse] = []
    user_audio_base64: str | None = None
    # Evaluation
    transcription: str = ""
    pronounciation_scores: PronounciationScores = PronounciationScores()
    semantic_evaluation: SemanticEvaluation = SemanticEvaluation()
    # Output
    status: Literal["pass", "fail", "pending"] = "pending"
    performance_reflection: str = ""
    feedback_text: str | None = None
    feedback_audio_base64: str | None = None


class VoiceTutorExplainInput(BaseModel):
    query: str
    question: str
    language: AvailableLanguage
    dialect: AvailableDialect | None = None
    vocab_words: List[VocabWordResponse]
    transcription: str
    pronounciation_scores: PronounciationScores
    semantic_evaluation: SemanticEvaluation
    status: Literal["pass", "fail"]
    performance_reflection: str
    previous_feedback: List[str]

class VoiceTutorExplainOutput(BaseModel):
    response_text: str | None = None


class VoiceTutorTTSInput(BaseModel):
    text: str = ""


class VoiceTutorTTSOutput(BaseModel):
    response_audio_base64: str | None = None

