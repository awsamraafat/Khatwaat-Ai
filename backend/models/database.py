from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

def get_supabase_client() -> Client:
    """Returns a Supabase client using the anon key (respects RLS)."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_admin() -> Client:
    """Returns a Supabase client using the service role key (bypasses RLS)."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
