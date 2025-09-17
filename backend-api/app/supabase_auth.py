import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseAuthService:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info"""
        try:
            user = self.supabase.auth.get_user(token)
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "name": user.user.user_metadata.get("full_name", user.user.email),
                    "is_admin": user.user.user_metadata.get("is_admin", False)
                }
            return None
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.supabase.auth.admin.get_user_by_id(user_id)
            if response and response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("full_name", response.user.email),
                    "is_admin": response.user.user_metadata.get("is_admin", False)
                }
            return None
        except Exception as e:
            print(f"Get user failed: {e}")
            return None

# Global instance
supabase_auth = SupabaseAuthService()
