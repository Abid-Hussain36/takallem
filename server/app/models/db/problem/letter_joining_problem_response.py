from pydantic import BaseModel
from typing import List


class LetterJoiningProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    word: str
    letter_list: List[str]

