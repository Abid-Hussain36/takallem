from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.supabase import get_supabase_client
from typing import Dict


security = HTTPBearer()


# This necessitates that the router endpoint that calls this function passes in a valid Auth bearer token
def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Returns the email from the authenticated token"""
    token = credentials.credentials

    try:
        supabase_client = get_supabase_client()
        user = supabase_client.auth.get_user(token) # This actually validates if the token is valid

        if not user.user or not user.user.email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user.user.email
    except Exception as e:
        # Log the actual error for debugging
        print(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {str(e)}"
        )
