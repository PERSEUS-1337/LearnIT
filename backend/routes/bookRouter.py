from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List

from models.books import Book, BookUpdate
from controllers.book_controller import create_book, list_books, find_book, update_book, delete_book
router = APIRouter()


# POST book
@router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book_route(request: Request, book: Book = Body(...)):
    return create_book(request, book)

# GET book
@router.get("/", response_description="List all books", response_model=List[Book])
def list_books_route(request: Request):
    return list_books(request)


# GET book {id}
@router.get("/{id}", response_description="Get a single book by id", response_model=Book)
def find_book_route(id: str, request: Request):
    return find_book(id, request)


# PUT (update) book {id}
@router.put("/{id}", response_description="Update a book", response_model=Book)
def update_book_route(id: str, request: Request, book: BookUpdate = Body(...)):
    return update_book(id, request, book)


@router.delete("/{id}", response_description="Delete a book")
def delete_book_route(id: str, request: Request, response: Response):
    return delete_book(id, request, response)
