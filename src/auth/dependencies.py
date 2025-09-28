from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi import status
from src.auth.utils import decode_token
from fastapi import Request
from src.db.redis import token_in_blocklist


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
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Missing Authorization header"
                )
            
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or expired",
                    "resolution":"Please get new token"
                }
            )

        token_data = decode_token(token) if token else None

        if token_data and await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or has been revoked",
                    "resolution":"Please get new token"
                }
            )

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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please provide an access token",)


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict | None) -> None:
        if token_data and not token_data.get("refresh"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please provide a refresh token",)