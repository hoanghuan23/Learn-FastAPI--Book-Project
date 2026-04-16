from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import models
from app.schema.book import Book, BookCreate, BookUpdate

router = APIRouter()

@router.get("/")
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
    return {"message: list_books"}