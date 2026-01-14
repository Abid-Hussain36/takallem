from typing import Union
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db.user.user_response import UserResponse
from app.db.database import get_db
from app.models.auth.signup_request import SignupRequest
from app.services.user_service import UserService
from app.utils.di import get_user_service


user_router = APIRouter()


@user_router.post("/create", response_model=UserResponse)
def create_user(
    user_data: SignupRequest,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return service.create_user(db, user_data)


@user_router.get("/{id}", response_model=Union[UserResponse, None])
def get_user(
    id: int,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> Union[UserResponse, None]:
    user = service.get_user_by_id(db, id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user