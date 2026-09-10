from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email : EmailStr
    password : str
    full_name : str


class UserResponse(BaseModel):
    id : int
    email : EmailStr
    full_name : str

    model_config = {
        "from_attributes" : True # sqlalchemy will give object not dictionary. pydantic needs to know that it can construct the response schema from object attributes.
    }


class UserUpdate(BaseModel):

    full_name : str 


class Token(BaseModel):
    access_token : str
    token_type : str

