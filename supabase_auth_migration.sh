#!/bin/bash

echo "🚀 SUPABASE AUTH MIGRATION - STARTING..."

# Step 1: Install Supabase CLI
echo "📦 Installing Supabase CLI..."
npm install -g supabase

# Step 2: Install Supabase dependencies
echo "📦 Installing Supabase dependencies..."
cd frontend-lexleaks
npm install @supabase/supabase-js
cd ../backend-api
pip install supabase
cd ..

# Step 3: Create environment files
echo "🔧 Creating environment files..."

# Frontend environment
cat > frontend-lexleaks/.env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Backend environment
cat >> backend-api/.env << 'EOF'

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
EOF

echo "✅ Migration setup complete!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to https://supabase.com/dashboard"
echo "2. Create a new project or use existing"
echo "3. Get your project URL and keys"
echo "4. Update the .env files with your actual values"
echo "5. Run: supabase login"
echo "6. Run: supabase link --project-ref YOUR_PROJECT_REF"
echo "7. Run: supabase start"
echo ""
echo "🎯 This will eliminate all OAuth complexity!"
