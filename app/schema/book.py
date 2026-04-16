from pydantic import BaseModel
from datetime import datetime

from app.schema.author import Author
from app.schema.category import Category

class BookBase(BaseModel):
    title: str
    description: str
    published_year: str
    category_id: str
    author_id: str


class BookCreate(BookBase):
    """Schema for create Book"""
    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    category_id: int | None = None
    author_id: int | None = None


class BookUpdate(BaseModel):
    """Schema for update Book"""
    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    category_id: int | None = None
    author_id: int | None = None


class BookInDBBase(BookBase):
    id: int
    title: str
    description: str
    published_year: int
    author_id: int
    cover_image: str | None = None
    created_at = datetime
    update_at = datetime

    class Config:
        orm_mode = True


class Book(BookInDBBase):
    """Schema return for client"""
    author = Author
    category = Category
