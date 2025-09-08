-- ============================================
-- LexLeaks Database Schema - Initial Setup
-- ============================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Create Tables
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Posts table (with all fields from migrations)
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    slug VARCHAR(250) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL 
        CHECK (status IN ('draft', 'published', 'archived')),
    verification_status VARCHAR(20) DEFAULT 'unverified' NOT NULL 
        CHECK (verification_status IN ('unverified', 'verified', 'disputed')),
    category VARCHAR(50),
    document_url VARCHAR(500),
    author_id INTEGER NOT NULL REFERENCES users(id),
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Impacts table
CREATE TABLE IF NOT EXISTS impacts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(50) NOT NULL 
        CHECK (type IN ('legal_action', 'policy_change', 'investigation', 'resignation', 'reform')),
    status VARCHAR(20) DEFAULT 'pending' NOT NULL 
        CHECK (status IN ('pending', 'in_progress', 'completed')),
    post_id INTEGER NOT NULL REFERENCES posts(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Push subscriptions table
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    endpoint VARCHAR UNIQUE NOT NULL,
    p256dh VARCHAR NOT NULL,
    auth VARCHAR NOT NULL,
    user_agent VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    notify_new_posts BOOLEAN DEFAULT TRUE,
    notify_updates BOOLEAN DEFAULT TRUE,
    notify_weekly_digest BOOLEAN DEFAULT FALSE
);

-- ============================================
-- Create Indexes for Performance
-- ============================================

-- Posts indexes
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_verification_status ON posts(verification_status);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_published_at ON posts(published_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- Impacts indexes
CREATE INDEX IF NOT EXISTS idx_impacts_post_id ON impacts(post_id);
CREATE INDEX IF NOT EXISTS idx_impacts_type ON impacts(type);
CREATE INDEX IF NOT EXISTS idx_impacts_status ON impacts(status);
CREATE INDEX IF NOT EXISTS idx_impacts_date ON impacts(date DESC);

-- Push subscriptions indexes
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_id ON push_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_is_active ON push_subscriptions(is_active);

-- ============================================
-- Create Triggers for Updated_at
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_posts_updated_at ON posts;
CREATE TRIGGER update_posts_updated_at 
    BEFORE UPDATE ON posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_impacts_updated_at ON impacts;
CREATE TRIGGER update_impacts_updated_at 
    BEFORE UPDATE ON impacts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_push_subscriptions_updated_at ON push_subscriptions;
CREATE TRIGGER update_push_subscriptions_updated_at 
    BEFORE UPDATE ON push_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Insert Admin User
-- ============================================

-- Create admin user (password is 'LexLeaks2024!')
-- Hash generated using bcrypt with 12 rounds
INSERT INTO users (username, hashed_password, is_admin) 
VALUES ('admin', '$2b$12$mB.W4Ioh8pfUK66O0vFiJuaDR7vqV0BgIXFC1CCAmpqRq3lBvaMI6', true)
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- Sample Data for Testing
-- ============================================

-- Insert a sample post for testing
INSERT INTO posts (
    title, 
    slug, 
    content, 
    excerpt, 
    status, 
    verification_status,
    category,
    author_id,
    published_at
) VALUES (
    'Welcome to LexLeaks',
    'welcome-to-lexleaks',
    '<h1>Welcome to LexLeaks</h1><p>This is your first article. You can edit or delete this post from the admin panel.</p><p>LexLeaks is a platform for exposing legal industry misconduct and promoting transparency.</p><blockquote><p>"Sunlight is said to be the best of disinfectants." - Louis Brandeis</p></blockquote><p>Use the admin panel to create, edit, and publish your articles. When you publish an article, it will automatically appear on the public homepage with our vintage newspaper styling.</p>',
    'Welcome to LexLeaks - your platform for legal transparency and accountability.',
    'published',
    'verified',
    'corporate',
    1,
    NOW()
)
ON CONFLICT (slug) DO NOTHING;

-- Get the post ID for the impact
DO $$
DECLARE
    post_id_var INTEGER;
BEGIN
    SELECT id INTO post_id_var FROM posts WHERE slug = 'welcome-to-lexleaks' LIMIT 1;
    
    IF post_id_var IS NOT NULL THEN
        -- Insert a sample impact for the welcome post
        INSERT INTO impacts (
            title,
            description,
            date,
            type,
            status,
            post_id
        ) VALUES (
            'Platform Launch',
            'LexLeaks platform successfully launched and operational, providing a secure platform for legal industry transparency.',
            NOW(),
            'reform',
            'completed',
            post_id_var
        )
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
