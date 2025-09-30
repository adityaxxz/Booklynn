# from fastapi import FastAPI
# from src.routes import book_router

# version = "v1"
# app = FastAPI(title="Booklynn", description="A Restful API for a book review web service")
# app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])

from src.errors import register_all_errors
import logging
from contextlib import asynccontextmanager
from src.db.main import initdb

from fastapi import FastAPI
from src.routesv2 import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from .middleware import register_middleware

# the lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

version="v1"

app = FastAPI(
    title="Booklynn",
    description="A REST API for a book review web service",
    version=version,
    lifespan=lifespan
)

register_all_errors(app)
register_middleware(app)


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

app.include_router(
    review_router,
    prefix="/review",
    tags=['review']
)