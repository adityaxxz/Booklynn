from .schema import ReviewCreateModel
from .service import ReviewService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.db.main import get_session
from src.auth.dependencies import RoleChecker, get_current_user


review_service = ReviewService()
review_router = APIRouter()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["admin", "user"]))


@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session:AsyncSession = Depends(get_session)):
    books = await review_service.get_all_reviews(session)
    return books

@review_router.get("/book/{book_uid}", dependencies=[user_role_checker])
async def get_review(review_uid:str, session: AsyncSession = Depends(get_session)):
    book = await review_service.get_review(review_uid, session)

    if not book: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") 
    return book


@review_router.post("/book/{book_uid}", dependencies=[user_role_checker])
async def add_review(book_uid: str, review_data: ReviewCreateModel, curr_user: User=Depends(get_current_user), session:AsyncSession=Depends(get_session)):
    
    new_review = await review_service.add_review_to_book(
                        user_email=curr_user.email,
                        book_uid=book_uid,
                        review_data=review_data, 
                        session=session)

    return new_review


@review_router.delete("/{review_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_role_checker])
async def delete_review(review_uid: str, curr_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await review_service.delete_review(review_uid=review_uid, user_email=curr_user.email, session=session)

    return None


