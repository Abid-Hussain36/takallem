from pydantic import BaseModel


class DictationProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    word: str
    word_audio: str

