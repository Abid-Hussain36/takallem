from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.dictation_problem_response import DictationProblemResponse


class DictationProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    problem_count: int
    problems: List[DictationProblemResponse]

