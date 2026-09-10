from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService
from app.dependencies.auth import get_current_user
from app.models.user import User



router = APIRouter( # creates a sub-router
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data : UserCreate,
    db : AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try :
        user = await service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )



@router.get(
        "/me",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user : User = Depends(get_current_user),
):
    return current_user



@router.patch(
    "/update_user",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update(
    user_data : UserUpdate,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = UserService(db)

    return await service.update_user(
        full_name=user_data.full_name,
        user_data=current_user, # User object
    )