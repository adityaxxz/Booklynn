from fastapi import APIRouter, Depends, status
from .schema import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from src.auth.utils import verify_password, create_access_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import AccessTokenBearer, RefreshTokenBearer
from src.db.redis import add_jti_to_blocklist, token_in_blocklist


auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):

    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User with email already exists",)

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

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Or Password")


@auth_router.post("/refresh")
async def get_refresh_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_time = token_details.get("exp")

    if expiry_time and datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(user_data=token_details.get("user") or {})

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")



@auth_router.get("/logout")
async def logout_user_revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    
    jti = token_details.get("jti")

    if not jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token not found")

    await add_jti_to_blocklist(jti)

    return JSONResponse(content={"message": "Logged out successfully, Token revoked successfully"}, status_code=status.HTTP_200_OK)
