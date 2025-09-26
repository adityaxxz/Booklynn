# from fastapi import FastAPI, status, HTTPException, APIRouter
# from fastapi.responses import JSONResponse
# from src.schema import Book, BookUpdate
# import json

# book_router = APIRouter()

# def load_data():
#     with open("src/books.json", "r") as f:
#         return json.load(f)
    
# def write_data(data):
#     with open("src/books.json", "w") as f:
#         json.dump(data, f)

# @book_router.get("/")
# async def home():
#     return {'message': "Homepage",
#             "status": "OK",}


# @book_router.get("/books")
# async def get_all_books():
#     data = load_data()
#     return data

# @book_router.post("/books", status_code=status.HTTP_201_CREATED)
# async def create_book(book_data: Book) -> dict:
#     new_book = book_data.model_dump()   # convert to dict
#     data = load_data()

#     ids = {book["id"] for book in data}

#     if new_book["id"] in ids:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="book_id exists in data")
    
#     data.append(new_book)
#     write_data(data)
#     return {"message": "New Book created", "book": new_book}


# @book_router.get("/view/{book_id}")
# async def get_book(book_id: int) -> dict:
#     data = load_data()
#     for book in data:
#         if book["id"] == book_id:
#             return book

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌Book not found")


# @book_router.patch("/update/{book_id}")
# async def update_book(book_id: int, new_data: BookUpdate) -> dict:
#     data = load_data()

#     for book in data:
#         if book["id"] == book_id:
#             update_fields = new_data.model_dump(exclude_unset=True)
#             for key,val in update_fields.items():
#                 book[key] = val

#             write_data(data)
#             return book
        

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌Book not found")


# @book_router.delete("/delete/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete(book_id: int):
#     data = load_data()

#     for i, book in enumerate(data):
#         if book["id"] == book_id:
#             print(i, "", book)
#             del data[i]
#             write_data(data)
#             return
    
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌Book not found")
    

