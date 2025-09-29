from src.db.models import User
from .schema import UserCreateModel
from .utils import generate_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        
        # Remove password from dict as it's not a field in User model
        password = user_data_dict.pop("password")
        
        # Create user with remaining fields
        new_user = User(**user_data_dict)
        
        # Set the hashed password
        new_user.password_hash = generate_password_hash(password)

        session.add(new_user)
        await session.commit()

        return new_user

    