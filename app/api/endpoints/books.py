from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db
from app import models
from app.schema.book import Book, BookCreate, BookUpdate

router = APIRouter()

@router.get("/", response_model=List[Book])
def list_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    author_id: int | None = Query(None),
    category_id: int | None = Query(None),
    year: int | None = Query(None),
    keyword: int | None = Query(None),

):
    """"
    Get list books , include filter
    - author_id
    - category_id
    - year (published_year)
    - keyword (search in title or desc)
    """
    mb = models.Book
    query = db.query(mb)
    if author_id is not None:
        query = query.filter(mb.author_id == author_id)
    if category_id is not None:
        query = query.filter(mb.category_id == category_id)
    if year is not None:
        query = query.filter(mb.published_year == year)
    if keyword is not None:
        like_pattern = f"%{keyword}"
        query = query.filter(
            or_(
                mb.title.ilike(like_pattern),
                mb.description.ilike(like_pattern)
            )
        )
    books = query.offset(skip).limit(limit).all()
    return books