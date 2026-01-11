from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem_set.vocab_listening_problem_set_response import VocabListeningProblemSetResponse


class VocabListeningProblemSetsResponse(BaseModel):
    id: int
    resource_type: ResourceType
    set_limit: int
    problem_sets: List[VocabListeningProblemSetResponse]

