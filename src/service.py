from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from src.models import Book
from src.schema import BookCreate, BookUpdate
from datetime import datetime
import uuid


class BookService:
    """
    This class provides methods to create, read, update and delete books from the db.
    """
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    # async def create_book(self, book_data: BookCreate, session:AsyncSession):
    #     # Create a new book
    #     # Args -> book_data (BookCreateModel): data to create a new
    #     # Returns -> Book: the new book

    #     data_dict = book_data.model_dump()
        
    #     # Generate a UUID for the new book
    #     data_dict['uid'] = str(uuid.uuid4())
        
    #     new_book = Book(**data_dict)

    #     new_book.year = str(data_dict['year'])

    #     session.add(new_book)
    #     await session.commit()

    #     return new_book

    async def get_book(self, book_uid: str, session: AsyncSession):
        stmt = select(Book).where(Book.uid == book_uid)
        res = await session.execute(stmt)

        book = res.scalar_one_or_none()   #fetches the first scalar result or None

        return book


    async def update_book(self, book_uid: str, update_data: BookUpdate, session: AsyncSession):
        
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump(exclude_unset=True)

            for key, val in update_data_dict.items():
                if val is not None:  # Only update non-None values
                    setattr(book_to_update, key, val)    #correct way for SQLAlchemy model instances
            
            book_to_update.updated_at = datetime.now()
            await session.commit()
            return book_to_update
        
        else: 
            return None

    async def delete_book(self, book_uid:str, session: AsyncSession):

        book_to_del = await self.get_book(book_uid, session)

        if book_to_del is not None:
            await session.delete(book_to_del)
            await session.commit()
            return {}
        
        else: 
            return None


#? Updating the Service to include the user_uid, ensuring each book is associated with the currently authenticated user's user_uid

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        stmt = (select(Book).where(Book.user_uid == user_uid))
        
        res = await session.execute(stmt)

        return res.all()

    async def create_book(self, data: BookCreate, user_uid: str, session: AsyncSession):
        book_data_dict = data.model_dump()

        new_book = Book(**book_data_dict)

        new_book.year = str(book_data_dict['year'])

        new_book.user_uid = uuid.UUID(user_uid) if user_uid else None
        session.add(new_book)
        await session.commit()
        return new_book

