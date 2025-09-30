from fastapi import APIRouter, Depends, status, Body, BackgroundTasks
from src.celery_task import send_email
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from .schema import PasswordResetConfirmModel, PasswordResetRequestModel, UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import generate_password_hash, verify_password, create_access_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import (AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleChecker)
from src.db.redis import add_jti_to_blocklist, token_in_blocklist
from src.db.models import User
from sqlmodel import select
from uuid import UUID
from src.auth.schema import EmailModel
from src.mail import mail, create_message
from src.auth.utils import create_url_safe_token, decode_url_safe_token
from src.config import Config


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

    # message=create_message(recipients=addresses, subject=subject, body=html)
    # await mail.send_message(message)
    send_email.delay(addresses, subject, html)

    return {"message": "Email Sent Successfully"}


#! New signup w email verification

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, bg_task: BackgroundTasks, session: AsyncSession = Depends(get_session),):
    email = user_data.email
    user_exists = await user_service.get_user_by_email(email, session)
    if user_exists:
        raise UserAlreadyExists()

    new_user  = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/auth/verify/{token}"

    html_message = f"""
    <h3>Welcome to Booklynn! Verify your Email for Signup</h3>
    <p>Please click this <a href="{link}">link</a> to verify your email.</p>
    <br></br>
    <p>Thanks.</p>
    """
    subject="Verify your Email for Booklynn"

    # message = create_message(recipients=[email], subject="Verify your Email for Booklynn", body=html_message)
    # await mail.send_message(message)
    # bg_task.add_task(mail.send_message, message)

    send_email.delay([email], subject, html_message)

    return {
        "message": "Account Created Successfully! Check email to verify the account.",
        "user": new_user,
    }

@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email") if token_data else None

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account Verified Successfully!"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error Occurred During Verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )



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


#! Password reset routes

@auth_router.post("/password-reset")
async def password_reset(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h3>Reset Your Password </h3>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Booklynn Account Password"
    # maybe, implement some background task so tht the current impl doesnt block the req until SMTP call finishes
    # using BAckgroud tasks will make the api respond immediately while the email is sent in the bg
    # this impl is synchronous from client perspective

    # message = create_message(recipients=[email], subject=subject, body=html_message)
    # await mail.send_message(message)

    send_email.delay([email], subject, html_message) #sends email in the background

    return JSONResponse(content= {
        "message": "Please check your email to reset your password.",
    }, status_code=status.HTTP_200_OK,)


@auth_router.post("/password-reset-confirm/{token}")
async def password_reset_confirm(token: str, passwords: PasswordResetConfirmModel, session: AsyncSession= Depends(get_session)):
    
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user: raise UserNotFound()

        pwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": pwd_hash}, session)

        return JSONResponse(
            content = {"message": "Password Reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content= {"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )