from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# for book post request validation
class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1900, lt=2025)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2000,
            }
        }
    }


LITERATURE = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 5, 2000),
    Book(2, "Be Fast with FastAPI", "codingwithroby", "A great book!", 5, 2002),
    Book(3, "Master Endpoints", "codingwithroby", "A awesome book!", 5, 2019),
    Book(4, "HP1", "Author 1", "A awesome book!", 2, 2022),
    Book(5, "HP2", "Author 2", "A awesome book!", 3, 1975),
    Book(6, "HP3", "Author 3", "A awesome book!", 1, 1945),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_books():
    return LITERATURE


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(book_id: int = Path(gt=0)):
    for book in LITERATURE:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/book/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in LITERATURE:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/published_date/", status_code=status.HTTP_200_OK)
async def get_book_by_published_date(published_date: int = Query(gt=1900, lt=2025)):
    books_to_return = []
    for book in LITERATURE:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    LITERATURE.append(find_book_id(new_book))


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(LITERATURE)):
        if LITERATURE[i].id == book.id:
            LITERATURE[i] = book
            book_changed = True

    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(LITERATURE)):
        if LITERATURE[i].id == book_id:
            LITERATURE.pop(i)
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


def find_book_id(book: Book):
    book.id = 1 if len(LITERATURE) == 0 else LITERATURE[-1].id + 1
    return book
