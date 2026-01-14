from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.supabase import get_supabase_client
from typing import Dict


security = HTTPBearer()


def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Returns the email from the authenticated token"""
    token = credentials.credentials

    supabase_client = get_supabase_client()
    user = supabase_client.auth.get_user(token)

    if not user.user or not user.user.email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user.user.email
