from pydantic import BaseModel
from typing import List
from app.models.db.vocab.vocab_word_response import VocabWordResponse


class VocabSpeakingProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    question: str
    vocab_words: List[VocabWordResponse]

