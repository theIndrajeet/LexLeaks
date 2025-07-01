from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Post Schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    verification_status: str = Field(default="unverified", pattern="^(unverified|verified|disputed)$")
    category: Optional[str] = Field(None, max_length=50)
    document_url: Optional[str] = Field(None, max_length=500)


class PostCreate(PostBase):
    pass
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    verification_status: Optional[str] = Field(None, pattern="^(unverified|verified|disputed)$")
    category: Optional[str] = Field(None, max_length=50)
    document_url: Optional[str] = Field(None, max_length=500)
    published_at: Optional[datetime] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v


class PostResponse(PostBase):
    id: int
    slug: str
    author_id: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    author: UserResponse
    
    class Config:
        from_attributes = True


class PostSummary(BaseModel):
    """Lightweight post schema for listing pages"""
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    status: str
    verification_status: str
    category: Optional[str]
    document_url: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    author: UserResponse
    
    class Config:
        from_attributes = True


class PostWithCounts(PostSummary):
    """Post summary with additional counts"""
    impact_count: int = 0
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Utility function to generate slug from title
def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


# Impact Schemas
class ImpactBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    date: datetime
    type: str = Field(..., pattern="^(legal_action|policy_change|investigation|resignation|reform)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")


class ImpactCreate(ImpactBase):
    post_id: int


class ImpactUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    date: Optional[datetime] = None
    type: Optional[str] = Field(None, pattern="^(legal_action|policy_change|investigation|resignation|reform)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")


class ImpactResponse(ImpactBase):
    id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True 