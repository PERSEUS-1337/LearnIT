from fastapi import Request, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models.books import Book, BookUpdate


def create_book(request: Request, book: Book = Body(...)):
    # Check if a book with the same title already exists
    existing_book = request.app.database["books"].find_one({"title": book.title})
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A book with the title '{book.title}' already exists."
        )

    # If no existing book, proceed with creating the new book
    book = jsonable_encoder(book)
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one(
        {"_id": new_book.inserted_id}
    )

    return created_book


def list_books(request: Request):
    books = list(request.app.database["books"].find(limit=100))

    if not books:
        return JSONResponse(content={"message": "No books available"}, status_code=status.HTTP_404_NOT_FOUND)

    return books


# GET book {id}
def find_book(id: str, request: Request):
    if (book := request.app.database["books"].find_one({"_id": id})) is not None:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")


# PUT (update) book {id}
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book = {k: v for k, v in book.dict().items() if v is not None}
    if len(book) >= 1:
        update_result = request.app.database["books"].update_one(
            {"_id": id}, {"$set": book}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

    if (existing_book := request.app.database["books"].find_one({"_id": id})) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")


def delete_book(id: str, request: Request, response: Response):
    delete_result = request.app.database["books"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")
