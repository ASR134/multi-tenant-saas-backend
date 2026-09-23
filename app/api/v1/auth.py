from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
# Request object gives access to client request

from app.db.session import get_db
from app.schemas.user import Token
from app.schemas.email import ResendVerificationRequest
from app.services.user import UserService
from app.utils.security import create_access_token
from app.utils.rate_limit import check_login_rate_limit, record_failed_login, reset_login_attempts


router = APIRouter( # creates sub router
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model = Token,
)
async def login(
    request : Request,
    form_data : OAuth2PasswordRequestForm = Depends(),
    db : AsyncSession = Depends(get_db)
):

    email = form_data.username.lower().strip()

    assert request.client is not None
    client_ip = request.client.host

    await check_login_rate_limit(
        email=email,
        ip = client_ip,
    )

    service = UserService(db)

    try:
        user = await service.authenticate_user(
            email=email, # email
            password=form_data.password,
        )
    except ValueError as e:
        await record_failed_login(
            email=email,
            ip = client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    await reset_login_attempts(
        email = email,
        ip = client_ip,
    )

    access_token = create_access_token(
        data={"sub" : str(user.id)}
    )

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }


@router.post(
    "/verify-email"
)
async def verify_email(
    token : str,
    db : AsyncSession = Depends(get_db),
):
    service = UserService(db)

    try:
        user = await service.verify_email(token)

        return {
            "message" : "Email verified successfully",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/resend-verification")
async def resend_verification(
    request : ResendVerificationRequest,
    db : AsyncSession = Depends(get_db),
):
    service = UserService(db)

    await service.resend_verification_email(request.email)

    return {
        "message" : "Verification email has been sent."
    }