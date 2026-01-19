from pydantic import BaseModel
from app.db.enums import Gender


class UpdateUserRequest(BaseModel):
    first_name: str | None
    last_name: str | None
    gender: Gender | None