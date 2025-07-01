from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model for authentication and authorship"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to posts
    posts = relationship("Post", back_populates="author")


class Post(Base):
    """Post model for articles/leaks"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500), nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # draft, published, archived
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    author = relationship("User", back_populates="posts") 