from pydantic import BaseModel
from typing import List


class ReadingComprehensionMCQProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    question: str
    question_audio: str
    correct_answer: str
    answer_choices: List[str]

