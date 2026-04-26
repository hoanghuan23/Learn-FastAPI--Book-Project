from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    status,
    Query,
    UploadFile,
)
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db
from app import models
from app.schema.book import Book, BookCreate, BookUpdate
from pathlib import Path
import uuid

router = APIRouter()

COVERS_DIR = Path("app/static/covers")
COVERS_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=List[Book])
def list_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    author_id: int | None = Query(None),
    category_id: int | None = Query(None),
    year: int | None = Query(None),
    keyword: str | None = Query(None),
):
    """ "
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
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(mb.title.ilike(like_pattern), mb.description.ilike(like_pattern))
        )
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    author = (
        db.query(models.Author).filter(models.Author.id == book_in.author_id).first()
    )

    if not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author with this ID does not exist",
        )

    category = (
        db.query(models.Category)
        .filter(models.Category.id == book_in.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this ID does not exist",
        )

    book = models.Book(
        title=book_in.title,
        description=book_in.description,
        published_year=book_in.published_year,
        author_id=book_in.author_id,
        category_id=book_in.category_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, book_up: BookUpdate, db: Session = Depends(get_db)):
    """Update an existing book"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if book_up.title is not None:
        book.title = book_up.title
    if book_up.description is not None:
        book.description = book_up.description
    if book_up.published_year is not None:
        book.published_year = book_up.published_year

    # if update author_id
    if book_up.author_id is not None and book_up.author_id != book.author_id:
        author = (
            db.query(models.Author)
            .filter(models.Author.id == book_up.author_id)
            .first()
        )
        if not author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author with this ID does not exist",
            )
        book.author_id = book_up.author_id

    # if update Category_id
    if book_up.category_id is not None and book_up.category_id != book.category_id:
        category = (
            db.query(models.Category)
            .filter(models.Category.id == book_up.category_id)
            .first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this ID does not exist",
            )
        book.category_id = book_up.category_id

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete an existing book"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db.delete(book)
    db.commit()


@router.post("/{book_id}/cover", response_model=Book)
async def upload_book_cover(
    book_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed.",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .jpg, .jpeg, and .png are allowed.",
        )

    contents = await file.read()
    max_size = 2 * 1024 * 1024  # 2MB
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum limit of 2MB.",
        )

    # Generate unique filename and save file
    filename = f"boook_{book_id}_{uuid.uuid4().hex}{ext}"
    file_path = COVERS_DIR / filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # update cover url to book
    book.cover_image = f"/static/covers/{filename}"
    db.add(book)
    db.commit()
    db.refresh(book)
    return book
