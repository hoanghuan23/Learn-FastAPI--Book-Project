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

@router.get("/{book_id}", response_model=Book)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db)
): 
    """Create a new category"""
    author = db.query(models.Author).filter(models.Author.id == book_in.author_id.name).first()


    if not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Author with this ID does not exist"
        )
    
    category = db.query(models.Category).filter(models.Category.id == book_in.category_id).first()


    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Category with this ID does not exist"
        )
    
    book = models.Book(
        title=book_in.title,
        description=book_in.description,
        published_year=book_in.published_year,
        author_id=book_in.author_id,
        category_id=book_in.category_id
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_up: CategoryUpdate,
    db: Session = Depends(get_db)
): 
    """Update an existing category"""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()


    if category_up.name is not None and category_up.name != category.name:
        existing =  db.query(models.Category).filter(models.Category.name == category_up.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Another category with this name already exists"
            )
        category.name = category_up.name    
    
    if category_up.description is not None:
        category.description = category_up.description
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
): 
    """Update an existing category"""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


    db.delete(category)
    db.commit()