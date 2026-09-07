from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):

    title : str
    description : str | None=None


class TaskUpdate(BaseModel):
    title : str | None = None
    description : str | None = None
    status : str | None = None
    version : int


class TaskResponse(BaseModel):
    id : int
    project_id : int
    title : str
    description : str | None
    status : str
    version : int
    created_at : datetime

    model_config ={
        'from_attributes' : True,
    }