from pydantic import BaseModel
from typing import List


class DiscriminationProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    word_audio: str
    incorrect_word_audio: str
    answer_choices: List[str]
    correct_answer: str

