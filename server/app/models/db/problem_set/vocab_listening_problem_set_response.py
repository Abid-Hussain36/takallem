from pydantic import BaseModel
from typing import List
from app.models.db.problem.vocab_listening_problem_response import VocabListeningProblemResponse


class VocabListeningProblemSetResponse(BaseModel):
    id: int
    set_number: int
    problem_count: int
    problems: List[VocabListeningProblemResponse]
