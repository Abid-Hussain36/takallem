from pydantic import BaseModel
from typing import List


class LetterWritingSequenceResponse(BaseModel):
    id: int
    lecture_id: int
    problem_id: int
    position: str
    sequence_images: List[str]

