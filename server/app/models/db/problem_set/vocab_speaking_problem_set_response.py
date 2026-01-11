from pydantic import BaseModel
from typing import List
from app.db.enums import Gender
from app.models.db.problem.vocab_speaking_problem_response import VocabSpeakingProblemResponse


class VocabSpeakingProblemSetResponse(BaseModel):
    id: int
    problem_count: int
    gender: Gender
    problems: List[VocabSpeakingProblemResponse]
