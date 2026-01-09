from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.vocab_reading_problem_response import VocabReadingProblemResponse


class VocabReadingProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    set_number: int
    set_limit: int
    problem_count: int
    problems: List[VocabReadingProblemResponse]

