# Supabase Deployment Guide for LexLeaks

## What I've Done for You:

1. **Created `.env.production` file** in `backend-api/` with your Supabase credentials:
   - Database URL with your project ID: `irxoxyjgdfyqluctpxk`
   - Password: `Indrajeet@002`
   
2. **Prepared the backend for deployment** - All code is ready to connect to Supabase

## What You Need to Do in Supabase:

### 1. Database Setup (In Supabase Dashboard)

1. **Go to your Supabase project**: https://app.supabase.com/project/irxoxyjgdfyqluctpxk

2. **Create the database tables** - Go to SQL Editor and run this:

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

-- Create index for slug lookups
CREATE INDEX idx_posts_slug ON posts(slug);

-- Create index for status filtering
CREATE INDEX idx_posts_status ON posts(status);
```

3. **Create the admin user** - Run this SQL:

```sql
-- Password is 'LexLeaks2024!' (already hashed)
INSERT INTO users (username, hashed_password, is_admin) 
VALUES ('admin', '$2b$12$mB.W4Ioh8pfUK66O0vFiJuaDR7vqV0BgIXFC1CCAmpqRq3lBvaMI6', true);
```

### 2. Database Connection Settings

1. **Get your connection string**:
   - Go to Settings → Database
   - Copy the "Connection string" URI
   - It should look like: `postgresql://postgres.irxoxyjgdfyqluctpxk:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres`

2. **Enable Row Level Security (Optional but recommended)**:
   - Go to Authentication → Policies
   - You can add policies later for extra security

### 3. Update Backend Configuration

The `.env.production` file I created needs to be updated with the correct connection pooler URL:

```bash
DATABASE_URL=postgresql://postgres.irxoxyjgdfyqluctpxk:Indrajeet@002@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

**Important**: Make sure to use the **Pooler** connection string (port 5432) for serverless deployments.

### 4. Deploy Backend to Railway

1. **Push your code to GitHub** (already done ✓)

2. **Create new Railway project**:
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `LexLeaks` repository
   - Choose the `backend-api` directory

3. **Set environment variables in Railway**:
   - Copy all variables from `.env.production`
   - Add them in Railway's Variables tab
   - **Important**: Generate a new SECRET_KEY for production!

4. **Configure Railway service**:
   - Set root directory: `/backend-api`
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 5. Deploy Frontend to Vercel

1. **Update frontend environment**:
   Create `.env.production` in `frontend-lexleaks/`:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app
   ```

2. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Import your GitHub repository
   - Set root directory: `frontend-lexleaks`
   - Add environment variable: `NEXT_PUBLIC_API_URL`

### 6. Update CORS Settings

Once deployed, update your backend's CORS to allow your Vercel frontend:

In Railway environment variables:
```
FRONTEND_URL=https://your-app.vercel.app
```

## Testing Your Deployment

1. **Test backend health**: 
   ```
   https://your-backend.railway.app/health
   ```

2. **Test API docs**:
   ```
   https://your-backend.railway.app/docs
   ```

3. **Test frontend**:
   ```
   https://your-app.vercel.app
   ```

## Troubleshooting

- **Database connection errors**: Make sure you're using the Pooler URL (port 5432)
- **CORS errors**: Update FRONTEND_URL in backend environment
- **Authentication errors**: Verify SECRET_KEY is the same in backend and properly set

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong database password
- [ ] Enable Row Level Security in Supabase
- [ ] Set up proper CORS origins
- [ ] Use HTTPS for all connections 