from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.problem.reading_comprehension_writing_problem_response import ReadingComprehensionWritingProblemResponse
from app.models.db.problem_set.reading_comprehension_text_response import ReadingComprehensionTextResponse


class ReadingComprehensionWritingProblemSetResponse(BaseModel):
    id: int
    resource_type: ResourceType
    text_id: int
    problem_count: int
    problems: List[ReadingComprehensionWritingProblemResponse]
    text: ReadingComprehensionTextResponse

