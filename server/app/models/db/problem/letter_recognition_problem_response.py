from pydantic import BaseModel
from typing import List


class LetterRecognitionProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    word: str
    answer_choices: List[str]
    correct_answer: str

