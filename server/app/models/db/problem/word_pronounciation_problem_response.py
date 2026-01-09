from pydantic import BaseModel


class WordPronounciationProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    question: str
    word: str
    word_audio: str

