from pydantic import BaseModel
from app.models.db.user.user_response import UserResponse


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    token_type: str