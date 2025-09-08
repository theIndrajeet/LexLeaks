#!/usr/bin/env python3
"""
Script to set a user as admin by email
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app.models import User

def set_admin_by_email(email: str):
    """Set a user as admin by their email address"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        # Update user to admin
        user.is_admin = True
        db.commit()
        
        print(f"✅ Successfully set user '{email}' as admin")
        print(f"   User ID: {user.id}")
        print(f"   Name: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Admin Status: {user.is_admin}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting admin: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = "heyjeetttt@gmail.com"
    print(f"🔧 Setting user '{email}' as admin...")
    success = set_admin_by_email(email)
    
    if success:
        print("\n🎉 Admin setup complete! You can now access the CRM.")
    else:
        print("\n💥 Failed to set admin. Please check the error above.")
