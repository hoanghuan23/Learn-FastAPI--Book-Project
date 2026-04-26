from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import authors, categories, books

app = FastAPI(
    title="Book Management API",
    description="A simple FastAPI application that serves static files.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(authors.router, prefix='/authors', tags=["authors"])
app.include_router(categories.router, prefix='/categories' ,tags=["categories"])
app.include_router(books.router, prefix='/books', tags=["books"])  

@app.get("/")

def read_root():
    return {"message": "Welcome to the Book Management API!"}   