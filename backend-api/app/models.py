from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model for authentication and authorship"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)  # Nullable for OAuth users
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # OAuth fields
    email = Column(String(255), unique=True, index=True, nullable=True)  # For OAuth users
    full_name = Column(String(255), nullable=True)  # For OAuth users
    google_id = Column(String(255), unique=True, nullable=True)  # Google OAuth ID
    profile_picture = Column(String(500), nullable=True)  # Profile picture URL
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'local', etc.
    
    # Relationship to posts
    posts = relationship("Post", back_populates="author")
    # Relationship to push subscriptions
    push_subscriptions = relationship("PushSubscription", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    """Post model for articles/leaks"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # draft, published, archived
    verification_status = Column(String(20), default="unverified", nullable=False)  # unverified, verified, disputed
    category = Column(String(50), nullable=True, index=True) # e.g., corporate, judicial, etc.
    document_url = Column(String(500), nullable=True)  # URL to associated PDF/document
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # AI-related fields
    ai_generated = Column(Boolean, default=False, nullable=True)
    ai_prompt = Column(Text, nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to user
    author = relationship("User", back_populates="posts")
    # Relationship to impacts
    impacts = relationship("Impact", back_populates="post", cascade="all, delete-orphan")


class Impact(Base):
    """Impact model for tracking real-world outcomes of posts"""
    __tablename__ = "impacts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    type = Column(String(50), nullable=False)  # legal_action, policy_change, investigation, resignation, reform
    status = Column(String(20), default="pending", nullable=False)  # pending, in_progress, completed
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to post
    post = relationship("Post", back_populates="impacts") 


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String, unique=True, nullable=False)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Notification preferences
    notify_new_posts = Column(Boolean, default=True)
    notify_updates = Column(Boolean, default=True)
    notify_weekly_digest = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="push_subscriptions")


class JobOpportunity(Base):
    """Job opportunity model for THE ENGINE"""
    __tablename__ = "job_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    company = Column(String(255), index=True, nullable=False)
    location = Column(String(255), nullable=True)
    work_type = Column(String(50), nullable=True)  # remote, hybrid, office, flexible
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD", nullable=False)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract, internship
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior
    practice_area = Column(String(100), nullable=True)  # corporate, criminal, ip, etc.
    firm_size = Column(String(50), nullable=True)  # boutique, mid-size, big-law
    practice_type = Column(String(50), nullable=True)  # litigation, transactional, regulatory
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    application_url = Column(String(500), nullable=True)
    source = Column(String(100), nullable=False)  # indeed, linkedin, etc.
    source_url = Column(String(500), nullable=True)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    expires_date = Column(DateTime(timezone=True), nullable=True)
    quality_score = Column(Float, nullable=True)
    is_remote = Column(Boolean, default=False, nullable=False)
    is_hybrid = Column(Boolean, default=False, nullable=False)
    is_office = Column(Boolean, default=False, nullable=False)
    gemini_enhanced = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 