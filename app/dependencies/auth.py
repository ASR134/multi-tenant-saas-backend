from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.core.config import settings
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.models.user import User # model class
from app.models.membership import Membership # model class
from app.models.organization import Organization # model class
from app.services.organization import OrganizationService



oauth2_scheme = OAuth2PasswordBearer( # reads token from the valid Authorization : Bearer <token> header on the request
    tokenUrl = "/api/v1/auth/login", # token url used by swagger ui. 
)
# we click "Authorize" in Swagger UI.
# Swagger UI's JS sends a POST to tokenUrl (your /api/v1/auth/login) with the credentials we typed in.
# our login endpoint responds with {"access_token": "...", "token_type": "bearer"}.
# Swagger UI grabs access_token and stores it.
# On every subsequent request you fire from /docs, Swagger UI attaches the header Authorization: Bearer <access_token> for us automatically.

# in real frontend, we login and get the response and store the token somewhere like
# in localstorage/session storage/cookie and manually attach it to subsequent request.

async def get_current_user( # authenticates the user using JWT authentication
        token : str = Depends(oauth2_scheme),
        db : AsyncSession = Depends(get_db), 
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )

    try:
        payload = jwt.decode( # verify's the signature then returns payload.
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None: 
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user_repository = UserRepository(db)

    user = await user_repository.get_by_id(int(user_id))

    if user is None: # is user present in db?
        raise credentials_exception

    return user


