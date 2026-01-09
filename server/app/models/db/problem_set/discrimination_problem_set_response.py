from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.discrimination_problem_response import DiscriminationProblemResponse


class DiscriminationProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    problem_count: int
    problems: List[DiscriminationProblemResponse]

