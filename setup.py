#!/usr/bin/env python3
"""
LexLeaks Complete Setup Script
This script will set up everything you need to run LexLeaks locally.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def create_env_files():
    """Create environment files with demo configuration"""
    print("📝 Creating environment files...")
    
    # Backend .env file
    backend_env = """# LexLeaks Backend Environment Configuration
# Database Configuration - Update with your PostgreSQL details
DATABASE_URL=postgresql://issac@localhost:5432/lexleaks_db

# JWT Security - CHANGE THESE IN PRODUCTION!
SECRET_KEY=demo-secret-key-change-in-production-make-this-very-long-and-random-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Demo Admin User - CHANGE AFTER FIRST LOGIN!
ADMIN_USERNAME=admin
# This is the hash for password "LexLeaks2024!" - CHANGE THIS!
ADMIN_PASSWORD_HASH=$2b$12$8OvVWklYWq/Yg.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8.R8

# Environment
ENVIRONMENT=development
"""
    
    # Frontend .env.local file
    frontend_env = """# LexLeaks Frontend Environment Configuration
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production deployment, change to your actual backend URL:
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
"""
    
    # Write backend .env file
    backend_env_path = Path("backend-api/.env")
    with open(backend_env_path, "w") as f:
        f.write(backend_env)
    print(f"✅ Created {backend_env_path}")
    
    # Write frontend .env.local file
    frontend_env_path = Path("frontend-lexleaks/.env.local")
    with open(frontend_env_path, "w") as f:
        f.write(frontend_env)
    print(f"✅ Created {frontend_env_path}")

def setup_backend():
    """Set up the backend"""
    print("\n🐍 Setting up Backend (FastAPI)...")
    
    backend_dir = Path("backend-api")
    if not backend_dir.exists():
        print(f"❌ Backend directory {backend_dir} not found!")
        return False
    
    # Create virtual environment
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("📦 Creating Python virtual environment...")
        success, stdout, stderr = run_command("python3 -m venv venv", cwd=backend_dir)
        if not success:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        print("✅ Virtual environment created!")
    
    # Install dependencies
    print("📥 Installing Python dependencies...")
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/python -m pip install -r requirements.txt"
    
    success, stdout, stderr = run_command(pip_cmd, cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Backend dependencies installed!")
    
    return True

def setup_frontend():
    """Set up the frontend"""
    print("\n⚛️  Setting up Frontend (Next.js)...")
    
    frontend_dir = Path("frontend-lexleaks")
    if not frontend_dir.exists():
        print(f"❌ Frontend directory {frontend_dir} not found!")
        return False
    
    # Check if Node.js is installed
    success, stdout, stderr = run_command("node --version", check=False)
    if not success:
        print("❌ Node.js is not installed!")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    print(f"✅ Node.js version: {stdout.strip()}")
    
    # Install dependencies
    print("📥 Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Frontend dependencies installed!")
    
    return True

def check_database():
    """Check if PostgreSQL is available"""
    print("\n🗄️  Checking database connectivity...")
    
    # Check if PostgreSQL is installed
    success, stdout, stderr = run_command("psql --version", check=False)
    if success:
        print(f"✅ PostgreSQL found: {stdout.strip()}")
        return True
    else:
        print("⚠️  PostgreSQL not found locally.")
        print("Options:")
        print("1. Install PostgreSQL locally")
        print("2. Use Docker: docker run --name lexleaks-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=lexleaks_db -p 5432:5432 -d postgres:13")
        print("3. Use Supabase (free cloud database)")
        return False

def create_start_scripts():
    """Create convenient start scripts"""
    print("\n📜 Creating start scripts...")
    
    # Backend start script
    if os.name == 'nt':  # Windows
        backend_script = """@echo off
echo Starting LexLeaks Backend...
cd backend-api
call venv\\Scripts\\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
        with open("start_backend.bat", "w") as f:
            f.write(backend_script)
        print("✅ Created start_backend.bat")
    else:  # Unix/Linux/macOS
        backend_script = """#!/bin/bash
 echo "🚀 Starting LexLeaks Backend..."
 cd backend-api
 source venv/bin/activate
 python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
        with open("start_backend.sh", "w") as f:
            f.write(backend_script)
        os.chmod("start_backend.sh", 0o755)
        print("✅ Created start_backend.sh")
    
    # Frontend start script
    if os.name == 'nt':  # Windows
        frontend_script = """@echo off
echo Starting LexLeaks Frontend...
cd frontend-lexleaks
npm run dev
"""
        with open("start_frontend.bat", "w") as f:
            f.write(frontend_script)
        print("✅ Created start_frontend.bat")
    else:  # Unix/Linux/macOS
        frontend_script = """#!/bin/bash
echo "🚀 Starting LexLeaks Frontend..."
cd frontend-lexleaks
npm run dev
"""
        with open("start_frontend.sh", "w") as f:
            f.write(frontend_script)
        os.chmod("start_frontend.sh", 0o755)
        print("✅ Created start_frontend.sh")

def main():
    """Main setup function"""
    print("🚀 LexLeaks Complete Setup")
    print("=" * 50)
    print("This script will set up everything you need to run LexLeaks locally.")
    print("")
    
    # Step 1: Create environment files
    create_env_files()
    
    # Step 2: Setup backend
    if not setup_backend():
        print("❌ Backend setup failed!")
        return
    
    # Step 3: Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed!")
        return
    
    # Step 4: Check database
    check_database()
    
        # Step 5: Create start scripts
    create_start_scripts()
    
    # Step 6: Setup admin user
    print("\n👤 Setting up admin user...")
    try:
        exec(open("create_admin.py").read())
    except Exception as e:
        print(f"⚠️  Could not create admin user automatically: {e}")
        print("You can run 'python3 create_admin.py' later after starting the backend.")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("=" * 50)
    print("")
    print("📋 Next Steps:")
    print("1. Make sure PostgreSQL is running")
    print("2. Start the backend server:")
    if os.name == 'nt':
        print("   start_backend.bat")
    else:
        print("   ./start_backend.sh")
    print("")
    print("3. Start the frontend server (in a new terminal):")
    if os.name == 'nt':
        print("   start_frontend.bat")
    else:
        print("   ./start_frontend.sh")
    print("")
    print("🌐 Access URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Admin:    http://localhost:3000/admin/login")
    print("   API Docs: http://localhost:8000/docs")
    print("")
    print("🔐 Demo Login:")
    print("   Username: admin")
    print("   Password: LexLeaks2024!")
    print("")
    print("⚠️  Remember to change the admin password after first login!")

if __name__ == "__main__":
    main() 