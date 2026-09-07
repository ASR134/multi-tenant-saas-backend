from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import Token
from app.services.user import UserService
from app.utils.security import create_access_token


router = APIRouter( # creates sub router
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model = Token,
)
async def login(
    form_data : OAuth2PasswordRequestForm = Depends(),
    db : AsyncSession = Depends(get_db)
):

    service = UserService(db)

    user = await service.authenticate_user(
        email=form_data.username, # email
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={"sub" : str(user.id)}
    )

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }