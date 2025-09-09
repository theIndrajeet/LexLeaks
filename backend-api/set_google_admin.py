#!/usr/bin/env python3
"""
Set Google OAuth user as admin
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def set_google_admin():
    try:
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv('.env')
        
        from app.database import SessionLocal
        from app import models
        
        print("🚀 Setting up Google OAuth Admin User")
        print("=" * 40)
        
        db = SessionLocal()
        try:
            # Check if Google admin exists
            existing_admin = db.query(models.User).filter(models.User.email == "heyjeetttt@gmail.com").first()
            if existing_admin:
                if existing_admin.is_admin:
                    print("✅ Google admin user already exists and is admin!")
                    print(f"   Email: {existing_admin.email}")
                    print(f"   Name: {existing_admin.full_name}")
                    print(f"   Admin: {existing_admin.is_admin}")
                else:
                    # Make existing user admin
                    existing_admin.is_admin = True
                    db.commit()
                    print("✅ Google user promoted to admin!")
                    print(f"   Email: {existing_admin.email}")
                    print(f"   Name: {existing_admin.full_name}")
                    print(f"   Admin: {existing_admin.is_admin}")
                return
            
            # Create Google OAuth admin user
            print("👤 Creating Google OAuth admin user...")
            
            google_admin = models.User(
                email="heyjeetttt@gmail.com",
                full_name="Admin User",
                is_admin=True,
                oauth_provider="google",
                google_id="google_123456789"  # This will be updated on first login
            )
            
            db.add(google_admin)
            db.commit()
            db.refresh(google_admin)
            
            print("✅ Google OAuth admin user created successfully!")
            print("=" * 40)
            print("🔐 GOOGLE OAUTH ADMIN:")
            print(f"   Email: {google_admin.email}")
            print(f"   Name: {google_admin.full_name}")
            print(f"   Admin: {google_admin.is_admin}")
            print("=" * 40)
            print("🌐 Login at: http://localhost:3000/admin/login")
            print("   Use 'Continue with Google' button")
            
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the backend dependencies:")
        print("cd backend-api && pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("1. Database is running")
        print("2. .env file is configured correctly")

if __name__ == "__main__":
    set_google_admin()
