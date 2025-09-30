from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi import status
from src.errors import *
from src.auth.utils import decode_token
from fastapi import Request
from src.db.redis import token_in_blocklist
from fastapi import Depends
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.db.models import User
from typing import List, Any

user_service = UserService()

class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        # Try to get credentials from the parent class first
        try:
            creds = await super().__call__(request)
        except HTTPException:
            # If that fails, try to manually parse the Authorization header
            # This handles case sensitivity issues
            auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Missing Authorization header")
            
            if not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid Authorization header format"
                )
            
            # Create a mock credentials object
            from fastapi.security import HTTPAuthorizationCredentials
            creds = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=auth_header[7:]  # Remove "Bearer " prefix
            )

        token = creds.credentials if creds else None

        if not self.token_valid(token):
            raise InvalidToken()

        token_data = decode_token(token) if token else None

        if token_data and await token_in_blocklist(token_data['jti']):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data  # type: ignore

    def token_valid(self, token: str | None) -> bool:

        token_data = decode_token(token) if token else None

        return token_data is not None 

    def verify_token_data(self, token_data: dict | None):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict | None) -> None:
        if token_data and token_data.get("refresh"):
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict | None) -> None:
        if token_data and not token_data.get("refresh"):
            raise RefreshTokenRequired()



async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]   # token_details.get("user").get("email")

    user = await user_service.get_user_by_email(user_email, session)

    return user
    

#for Role Based Access Control
class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()