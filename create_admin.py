#!/usr/bin/env python3
"""
Create admin user for LexLeaks
Demo setup script - Change the password after first login!
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-api'))

def create_admin():
    try:
        from passlib.context import CryptContext
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv('backend-api/.env')
        
        from backend_api.app.database import SessionLocal, engine
        from backend_api.app import models
        
        print("🚀 Setting up LexLeaks Admin User")
        print("=" * 40)
        
        # Create tables
        print("📊 Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created!")
        
        db = SessionLocal()
        try:
            # Check if admin exists
            existing_admin = db.query(models.User).filter(models.User.username == "admin").first()
            if existing_admin:
                print("✅ Admin user already exists!")
                print(f"   Username: admin")
                print("   Password: (use existing password)")
                return
            
            # Demo credentials - CHANGE THESE AFTER FIRST LOGIN!
            demo_username = "admin"
            demo_password = "LexLeaks2024!"  # Strong demo password
            demo_email = "admin@lexleaks.demo"
            
            print(f"👤 Creating admin user with demo credentials...")
            
            # Hash password
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(demo_password)
            
            # Create admin user
            admin_user = models.User(
                username=demo_username,
                email=demo_email,
                hashed_password=hashed_password
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ Admin user created successfully!")
            print("=" * 40)
            print("🔐 DEMO LOGIN CREDENTIALS:")
            print(f"   Username: {demo_username}")
            print(f"   Password: {demo_password}")
            print(f"   Email: {demo_email}")
            print("=" * 40)
            print("⚠️  IMPORTANT: Change these credentials after first login!")
            print("🌐 Login at: http://localhost:3000/admin/login")
            
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the backend dependencies:")
        print("cd backend-api && pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("1. PostgreSQL is running")
        print("2. Database exists")
        print("3. .env file is configured correctly")

def generate_password_hash():
    """Helper function to generate password hash for manual use"""
    try:
        from passlib.context import CryptContext
        
        print("🔧 Password Hash Generator")
        print("=" * 30)
        
        password = input("Enter password to hash: ")
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash(password)
        
        print(f"Hash: {hashed}")
        print("Copy this hash to your .env file under ADMIN_PASSWORD_HASH")
        
    except ImportError:
        print("Install passlib first: pip install passlib[bcrypt]")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hash":
        generate_password_hash()
    else:
        create_admin() 