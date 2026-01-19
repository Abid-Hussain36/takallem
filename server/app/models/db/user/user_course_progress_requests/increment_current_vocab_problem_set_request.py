from pydantic import BaseModel


class IncrementCurrentVocabProblemSetRequest(BaseModel):
    id: int
    limit: int