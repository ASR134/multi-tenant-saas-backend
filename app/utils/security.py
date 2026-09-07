from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings # config object

password_hash = PasswordHash.recommended()


def hash_password(password : str) -> str:
    return password_hash.hash(password)


def verify_password(password : str,hashed_password : str) -> bool:
    return password_hash.verify(password,hashed_password)


def create_access_token(data : dict) -> str:
    to_encode = data.copy() # coz dictionary are mutable in python 

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp" : expire}) # payload

    encoded_jwt = jwt.encode( # PyJWT takes dict and converts it into JWT string which has three dot separated parts : header.payload.signature
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


    return encoded_jwt 

# header and payload are encoded not encrypted.Therefore don't put secrets in payload.
# signature is what protects .
# refresh token needs to be locked down more carefully than access token.