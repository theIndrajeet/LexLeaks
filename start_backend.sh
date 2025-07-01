#!/bin/bash
 echo "🚀 Starting LexLeaks Backend..."
 cd backend-api
 source venv/bin/activate
 python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
