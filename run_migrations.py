#!/usr/bin/env python3
"""Run Alembic migrations"""

import os
import sys
from alembic import command
from alembic.config import Config

def run_migrations():
    """Run pending migrations"""
    try:
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run upgrade to latest revision
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 