from pydantic import BaseModel


class ReadingComprehensionWritingProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    question_audio: str

