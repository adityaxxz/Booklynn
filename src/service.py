from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from src.models import Book
from src.schema import BookCreate, BookUpdate
from datetime import datetime
import uuid


class BookService:
    """
    This class provides methods to create, read, update and delete books.
    """

    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def create_book(self, book_data: BookCreate, session:AsyncSession):
        # Create a new book
        # Args -> book_data (BookCreateModel): data to create a new
        # Returns -> Book: the new book

        data_dict = book_data.model_dump()
        
        # Generate a UUID for the new book
        data_dict['uid'] = str(uuid.uuid4())
        
        new_book = Book(**data_dict)

        # It is correct to display only the year if your application only needs the year.
        # However, this line converts the year string to a datetime object, which may not be necessary
        # if your Book model expects a string or integer for the year.
        # If Book.year is a string or int, you can just assign it directly:
        new_book.year = str(data_dict['year'])

        session.add(new_book)
        await session.commit()

        return new_book

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


