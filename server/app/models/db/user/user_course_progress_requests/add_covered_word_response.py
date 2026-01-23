from pydantic import BaseModel


class AddCoveredWordResponse(BaseModel):
    coveredWordAdded: bool