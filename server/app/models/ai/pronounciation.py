from typing import Literal, List
from pydantic import BaseModel


class PronounciationResponse(BaseModel):
    status: Literal["pass", "fail"]
    transcription: str
    feedback: str
    mistake_tags: List[str]
    performance_reflection: str

class PronounciationExplainInput(BaseModel):
    query: str
    phrase: str
    status: Literal["pass", "fail"]
    transcription: str
    previous_feedback: List[str]
    mistake_tags: List[str]
    performance_reflection: str

class PronounciationExplainResponse(BaseModel):
    response: str
