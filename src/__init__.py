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

version="v2"

app = FastAPI(
    title="Booklynn",
    description="Booklynn is a modern RESTful API for discovering, reviewing, and sharing books. It provides endpoints for user authentication, book management, and community-driven reviews, enabling seamless integration for book-related web applications.",
    version=version,
    lifespan=lifespan,
    openapi_url=f"/{version}/openapi.json",
    docs_url=f"/{version}/docs",
    contact={
        "name": "adra",
        "url": "https://0xadra.site",
        "email": "adityaranjan5995@gmail.com"
    },
    redoc_url=f"/{version}/redoc",
)

register_all_errors(app)
register_middleware(app)


app.include_router(
    book_router,
    prefix=f"/{version}/books",
    tags=['books']
)

app.include_router(
    auth_router,
    prefix=f"/{version}/auth",
    tags=['auth']
)

app.include_router(
    review_router,
    prefix=f"/{version}/review",
    tags=['review']
)