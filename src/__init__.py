# from fastapi import FastAPI
# from src.routes import book_router

# version = "v1"
# app = FastAPI(title="Bookly", description="A Restful API for a book review web service")
# app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])

from fastapi import FastAPI
from src.routesv2 import book_router
from src.auth import auth_router
from contextlib import asynccontextmanager
from src.db.main import initdb


# the lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Server is starting...")
    await initdb()
    yield
    print("Server is stopping")

app = FastAPI(
    lifespan=lifespan # add the lifespan event to our application
)

app.include_router(
    book_router,
    prefix="/books",
    tags=['books']
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=['auth']
)