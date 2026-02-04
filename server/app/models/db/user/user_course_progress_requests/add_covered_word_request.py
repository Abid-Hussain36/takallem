from pydantic import BaseModel


class AddCoveredWordRequest(BaseModel):
    id: int
    word: str