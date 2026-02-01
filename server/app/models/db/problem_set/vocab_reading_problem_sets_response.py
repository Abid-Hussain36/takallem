from pydantic import BaseModel
from typing import List
from app.db.enums import AvailableDialect, ResourceType
from app.models.db.problem_set.vocab_reading_problem_set_response import VocabReadingProblemSetResponse


class VocabReadingProblemSetsResponse(BaseModel):
    id: int
    resource_type: ResourceType
    set_limit: int
    dialect: AvailableDialect | None = None
    problem_sets: List[VocabReadingProblemSetResponse]

