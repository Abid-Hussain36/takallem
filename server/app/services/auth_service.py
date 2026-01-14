from typing import Union, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.auth.signup_request import SignupRequest
from app.models.db.user.user_response import UserResponse
from app.models.auth.login_request import LoginRequest
from app.utils.supabase import get_supabase_client
from app.services.user_service import UserService
import logging
from app.models.auth.auth_response import AuthResponse

logger = logging.getLogger(__name__) # Creates a logger that's titled with the module being logged


class AuthService:
    def signup(self, user_data: SignupRequest, db: Session, service: UserService) -> AuthResponse:
        try:
            supabase_client = get_supabase_client()
            auth_response = supabase_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create auth user. Email might already be registered."
                )

            user = service.create_user(db, user_data)

            return AuthResponse(user=user, token=auth_response.session.access_token, token_type="bearer")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during signup: {str(e)}"
            )

    
    def login(self, user_data: LoginRequest, db: Session, service: UserService) -> AuthResponse:
        try:
            supabase_client = get_supabase_client()
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password."
                )

            user = service.get_user_by_email(db, user_data.email)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            return AuthResponse(user=user, token=auth_response.session.access_token, token_type="bearer")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during login: {str(e)}"
            )