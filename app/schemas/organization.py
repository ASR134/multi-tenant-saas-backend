from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):

    name : str


class OrganizationResponse(BaseModel):

    id : int
    name : str

    model_config = ConfigDict(from_attributes=True)