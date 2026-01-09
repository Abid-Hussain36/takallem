from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType


class LetterSpeakingLectureResponse(BaseModel):
    id: int
    resource_type: ResourceType
    letter: str
    content: List[str]
    letter_audio: str
    word_audios: List[str]

