from pydantic import BaseModel
from typing import List
from app.models.db.problem.vocab_reading_problem_response import VocabReadingProblemResponse


class VocabReadingProblemSetResponse(BaseModel):
    id: int
    set_number: int
    problem_count: int
    problems: List[VocabReadingProblemResponse]

