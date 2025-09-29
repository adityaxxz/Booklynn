import logging
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.service import BookService
from src.db.models import Review
from .schema import ReviewCreateModel


book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(self, user_email:str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(email=user_email, session=session)

            review_data_dict = review_data.model_dump()

            new_review = Review(**review_data_dict)

            if not book:
                raise HTTPException(detail="Book not found", status_code=status.HTTP_404_NOT_FOUND)

            if not user:
                raise HTTPException(detail="Book not found", status_code=status.HTTP_404_NOT_FOUND)

            # Set foreign keys explicitly as strings to match SQLite String(36) columns
            new_review.user_uid = str(user.uid)
            new_review.book_uid = str(book.uid)

            session.add(new_review)
            await session.commit()
            return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(detail="Oops... something went wrong!",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,)

    
    async def get_review(self, review_uid:str, session:AsyncSession):
        stmt = select(Review).where(Review.uid == review_uid)

        res = await session.exec(stmt)

        return res.first()

    async def get_all_reviews(self, session:AsyncSession):
        stmt = select(Review).order_by(desc(Review.created_at))

        res = await session.exec(stmt)

        return res.all()


    async def delete_review(self, review_uid: str, user_email: str, session: AsyncSession):

        user = await user_service.get_user_by_email(email=user_email, session=session)
        review = await self.get_review(review_uid, session)

        # # Allow delete if owner of the review, already impl in role checker
        # is_owner = str(review.user_uid) == str(user.uid)
        # if not is_owner:
        #     raise HTTPException(detail="Cannot delete this review", status_code=status.HTTP_403_FORBIDDEN)

        await session.delete(review)
        await session.commit()

        

    

        
