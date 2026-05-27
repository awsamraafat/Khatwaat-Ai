import os
from dotenv import load_dotenv

# Since we are running from the root directory, explicitly point to backend/.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# CORS origins - adjust for production
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# AI Engine defaults
DEFAULT_MAX_QUESTIONS = 20
DEFAULT_TARGET_SE = 0.3
DEFAULT_TIME_PER_QUESTION = 60
