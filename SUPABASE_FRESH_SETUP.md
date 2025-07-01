# Fresh Supabase Setup Guide for LexLeaks

## Step 1: Create New Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in:
   - Project name: `LexLeaks` (or any name you prefer)
   - Database Password: Choose a strong password WITHOUT special characters like @ to avoid URL encoding issues
   - Region: Choose closest to your users
4. Click "Create Project" and wait for setup

## Step 2: Note Your Project Details

After creation, you'll get:
- Project URL: `https://[YOUR-PROJECT-ID].supabase.co`
- Project ID: `[YOUR-PROJECT-ID]`
- Database Password: The one you just set

## Step 3: Get Database Connection String

1. Go to Settings → Database
2. Find "Connection string" → URI
3. Copy the connection string that looks like:
   ```
   postgresql://postgres.[YOUR-PROJECT-ID]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```

## Step 4: Create Database Tables

Go to SQL Editor in Supabase and run this SQL:

```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    author_id INTEGER REFERENCES users(id),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_posts_slug ON posts(slug);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published_at ON posts(published_at DESC);

-- Create admin user (password is 'LexLeaks2024!')
INSERT INTO users (username, hashed_password, is_admin) 
VALUES ('admin', '$2b$12$mB.W4Ioh8pfUK66O0vFiJuaDR7vqV0BgIXFC1CCAmpqRq3lBvaMI6', true);
```

## Step 5: Update Local Environment

Create/Update `backend-api/.env` with your new Supabase credentials:

```env
# Database
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-ID]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres

# JWT Secret (generate a secure one)
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=LexLeaks2024!

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

## Step 6: Test Database Connection

1. Activate virtual environment:
   ```bash
   cd backend-api
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Start the backend:
   ```bash
   cd backend-api
   uvicorn app.main:app --reload
   ```

3. Check:
   - http://localhost:8000/health - Should return {"status": "healthy"}
   - http://localhost:8000/docs - Should show API documentation

## Important Notes:

- **Use Pooler URL**: Always use the pooler connection (port 5432) for better performance
- **Avoid special characters in password**: To prevent URL encoding issues
- **Keep credentials secure**: Never commit .env files to Git
- **Test locally first**: Ensure everything works before deploying

## Next Steps:

1. Test admin login at http://localhost:3000/admin/login
2. Create some test posts
3. Deploy to production when ready 