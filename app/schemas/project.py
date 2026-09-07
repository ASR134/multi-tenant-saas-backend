from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):

    name : str
    description : str | None = None


class ProjectResponse(BaseModel):

    id : int
    organization_id : int
    name : str
    description : str|None
    version : int
    created_at : datetime

    model_config = {
        'from_attributes' : True,
    }


class ProjectUpdate(BaseModel):

    name : str | None=None
    description : str | None = None
    version : int