from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.word_pronounciation_problem_response import WordPronounciationProblemResponse


class WordPronounciationProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    problem_count: int
    problems: List[WordPronounciationProblemResponse]

