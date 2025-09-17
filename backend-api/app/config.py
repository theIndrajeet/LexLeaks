import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Admin configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "LexLeaks2024!")

# CORS configuration - Auto-detect environment
if os.getenv("K_SERVICE") or os.getenv("GOOGLE_CLOUD_PROJECT"):
    # Production environment
    FRONTEND_URL = "https://lexleaks.com"
else:
    # Development environment
    FRONTEND_URL = "http://localhost:3000"

# AI API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Indian Kanoon API
INDIAN_KANOON_API_KEY = os.getenv("INDIAN_KANOON_API_KEY")
