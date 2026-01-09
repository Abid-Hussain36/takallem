from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.vocab.vocab_word_response import VocabWordResponse


class VocabLectureResponse(BaseModel):
    id: int
    resource_type: ResourceType
    vocab_words: List[VocabWordResponse]

