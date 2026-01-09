from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.letter_writing_problem_response import LetterWritingProblemResponse


class LetterWritingProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    problem_count: int
    problems: List[LetterWritingProblemResponse]

