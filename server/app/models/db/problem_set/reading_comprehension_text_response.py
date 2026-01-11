from pydantic import BaseModel
from typing import List


class ReadingComprehensionTextResponse(BaseModel):
    id: int
    text_title: str
    text: List[str]

