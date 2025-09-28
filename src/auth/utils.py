import bcrypt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt 
from src.config import Config
import logging, uuid
from typing import Optional


def generate_password_hash(password: str) -> str:
    # Ensure password is within bcrypt limits (72 bytes max)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return hash_bytes.decode('utf-8')


def verify_password(password: str, hash: str) -> bool:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hash_bytes = hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_access_token(user_data: dict, expiry:timedelta=timedelta(minutes=15), refresh:bool =False) -> str:
    payload = {
        'user':user_data,
        'exp': datetime.now() + (expiry if expiry is not None else timedelta(minutes=60)),
        'refresh':refresh,
        'jti':str(uuid.uuid4())
    }

    token = jwt.encode(payload=payload, key=Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(jwt=token, key=Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return token_data
    
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    
    except Exception as e:
        logging.exception(e)
        return None