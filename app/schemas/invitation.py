from pydantic import BaseModel,EmailStr

from datetime import datetime

class InvitationCreate(BaseModel):
    email : EmailStr


class InvitationResponse(BaseModel):

    id : int
    organization_id : int
    email : EmailStr
    invited_by : int
    token : str
    status : str
    created_at : datetime
    expires_at : datetime

    model_config = {
        'from_attributes' : True,
    }
