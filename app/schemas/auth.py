from pydantic import BaseModel, EmailStr

class ResendVerificationRequest(BaseModel):
    email : EmailStr


class ForgetPasswordReset(BaseModel):
    email : EmailStr


class ResetPasswordRequest(BaseModel):
    token : str
    new_password : str