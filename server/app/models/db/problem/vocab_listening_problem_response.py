from pydantic import BaseModel
from typing import List
from app.models.db.vocab.vocab_word_response import VocabWordResponse


class VocabListeningProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    vocab_word_id: int
    answer_choices: List[str]
    vocab_word: VocabWordResponse

