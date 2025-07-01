#!/usr/bin/env python3
"""Simple script to verify Supabase database connection"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend-api/.env')

# Check if DATABASE_URL is set
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL not found in backend-api/.env")
    print("Please follow the setup guide in SUPABASE_FRESH_SETUP.md")
    sys.exit(1)

print("✅ DATABASE_URL found")
print(f"   URL pattern: postgresql://postgres.***:***@{database_url.split('@')[1].split('/')[0]}/***")

# Run the actual verification in the backend virtual environment
verification_script = """
import sys
sys.path.append('backend-api')

try:
    from app.database import engine, SessionLocal
    from app.models import User, Post
    from sqlalchemy import text, inspect
    
    # Try to connect
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
            
            # Check users
            with SessionLocal() as db:
                user_count = db.query(User).count()
                admin_exists = db.query(User).filter(User.username == "admin").first() is not None
                post_count = db.query(Post).count()
                
                print(f"✅ Users in database: {user_count}")
                print(f"✅ Admin user exists: {'Yes' if admin_exists else 'No'}")
                print(f"✅ Posts in database: {post_count}")
        else:
            print("⚠️  No tables found. Run the SQL script from SUPABASE_FRESH_SETUP.md")
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\\nPossible issues:")
    print("- Check if DATABASE_URL is correct")
    print("- Ensure Supabase project is active")
    print("- Verify password doesn't contain special characters")
    print("- Use the Pooler connection string (port 5432)")
"""

# Run verification using backend virtual environment
try:
    result = subprocess.run(
        ["backend-api/venv/bin/python3", "-c", verification_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
except Exception as e:
    print(f"❌ Failed to run verification: {e}")
    print("Make sure the backend virtual environment exists:")
    print("cd backend-api && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt") 