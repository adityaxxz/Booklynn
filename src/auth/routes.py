from fastapi import APIRouter, Depends, status, Body
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from .schema import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import verify_password, create_access_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import (AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleChecker)
from src.db.redis import add_jti_to_blocklist, token_in_blocklist
from src.db.models import User
from sqlmodel import select
from uuid import UUID
from src.mail import mail, create_message
from src.auth.schema import EmailModel 


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["admin"])

@auth_router.get("/me", response_model=UserBooksModel)
async def get_curr_user(user: User = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user

@auth_router.post("/send-mail")
async def send_mail(emails: EmailModel):
    addresses = emails.addresses

    html = "<h1>Welcome to Booklynn</h1>"
    subject = "Hello user, thankyou for using Booklynn"

    message=create_message(recipients=addresses, subject=subject, body=html)
    await mail.send_message(message)

    return {"message": "Email Sent Successfully"}



@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):

    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    return new_user


@auth_router.post("/login")
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)})

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=7),)

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise InvalidCredentials()


@auth_router.post("/refresh")
async def get_refresh_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_time = token_details.get("exp")

    if expiry_time and datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(user_data=token_details.get("user") or {})

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()



@auth_router.get("/logout")
async def logout_user_revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    
    jti = token_details.get("jti")

    if not jti:
        raise InvalidToken()

    await add_jti_to_blocklist(jti)

    return JSONResponse(content={"message": "Logged out successfully, Token revoked successfully"}, status_code=status.HTTP_200_OK)


@auth_router.delete("/users/{user_uid}")
async def delete_user(user_uid: str, session: AsyncSession = Depends(get_session)):
    # Support both hyphenated UUIDs and 32-char hex without hyphens
    try:
        normalized_uid = UUID(user_uid)
    except ValueError:
        try:
            normalized_uid = UUID(hex=user_uid)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid UUID format for user_uid")

    statement = select(User).where(User.uid == normalized_uid)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise UserNotFound()

    await session.delete(user)
    await session.commit()

    return JSONResponse(content={"message": "User deleted successfully", "uid": str(normalized_uid)}, status_code=status.HTTP_200_OK)
