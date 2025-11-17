"""
Database Schemas for Atmasakshi Foundation

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class Event(BaseModel):
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    date: datetime = Field(..., description="Event date and time")
    location: Optional[str] = Field(None, description="Event location")
    image_url: Optional[str] = Field(None, description="Image representing the event")
    tags: List[str] = Field(default_factory=list, description="Tags like meditation, service")


class Blogpost(BaseModel):
    title: str = Field(..., description="Blog post title")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, description="Short summary")
    content: str = Field(..., description="Full content (markdown supported)")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    author: Optional[str] = Field("Team Atmasakshi", description="Author name")
    published_at: datetime = Field(default_factory=datetime.utcnow)


class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str


class Volunteer(BaseModel):
    name: str
    email: EmailStr
    phone: str
    areas: List[str] = Field(..., description="Areas to volunteer")
    notes: Optional[str] = None


class Donation(BaseModel):
    upi_id: str
    qr_image_url: Optional[str] = None
    note: Optional[str] = Field(None, description="How donations are used")
