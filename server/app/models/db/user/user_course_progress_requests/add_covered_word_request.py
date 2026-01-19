from pydantic import BaseModel


class AddCoveredWordReqest(BaseModel):
    id: int
    word: str