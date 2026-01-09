from pydantic import BaseModel
from app.db.enums import AvailableDialect


class DialectResponse(BaseModel):
    id: int
    dialect: AvailableDialect
    image: str
    text_color: str