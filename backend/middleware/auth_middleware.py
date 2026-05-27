from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.database import get_supabase_client

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the JWT token from the Authorization header and returns user info.
    Uses Supabase Auth to verify the token.
    """
    token = credentials.credentials
    
    try:
        supabase = get_supabase_client()
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get profile data gracefully (handle PGRST116 if no profile row exists)
        try:
            profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
            role = profile.data.get("role", "student")
            full_name = profile.data.get("full_name", "")
        except BaseException:
            # Fallback if profile row is missing
            role = "student"
            full_name = ""
        
        return {
            "id": str(user.id),
            "email": user.email,
            "role": role,
            "full_name": full_name,
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Ensures the current user has admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
