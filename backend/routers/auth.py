from fastapi import APIRouter, HTTPException
from models.schemas import RegisterRequest, LoginRequest, AuthResponse
from models.database import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """Register a new user and bypass email confirmation using Admin API."""
    try:
        from models.database import get_supabase_admin, get_supabase_client
        supabase_admin = get_supabase_admin()
        supabase_client = get_supabase_client()
        
        # 1. Forcefully create and auto-confirm user with Admin API
        try:
            admin_response = supabase_admin.auth.admin.create_user({
                "email": req.email,
                "password": req.password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": req.full_name,
                    "role": req.role
                }
            })
        except Exception as e:
            # If user already exists, we can just try logging them in
            if "already registered" not in str(e).lower():
                raise
                
        # 2. Sign in normally to get the session token
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        user = auth_response.user
        session = auth_response.session
        
        if not user or not session:
            raise HTTPException(status_code=400, detail="Registration failed to generate session")
        
        return AuthResponse(
            access_token=session.access_token,
            user_id=str(user.id),
            email=user.email,
            role=req.role,
            full_name=req.full_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Login with email and password."""
    try:
        supabase = get_supabase_client()
        
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        user = auth_response.user
        session = auth_response.session
        
        if not user or not session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get profile gracefully
        try:
            profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
            role = profile.data.get("role", "student")
            full_name = profile.data.get("full_name", "")
        except Exception:
            role = "student"
            full_name = ""
        
        return AuthResponse(
            access_token=session.access_token,
            user_id=str(user.id),
            email=user.email,
            role=role,
            full_name=full_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
