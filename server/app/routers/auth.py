from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.db.user.user_response import UserResponse
from app.models.auth.signup_request import SignupRequest
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.auth.login_request import LoginRequest
from app.utils.di import get_auth_service, get_user_service
from app.services.user_service import UserService


auth_router = APIRouter()


@auth_router.post("/signup", response_model=UserResponse)
def signup(
    user_data: SignupRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    return auth_service.signup(user_data, db, user_service)


@auth_router.post("/login", response_model=UserResponse)
def login(
    user_data: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    return auth_service.login(user_data, db, user_service)