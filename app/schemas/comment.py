from pydantic import BaseModel

from datetime import datetime

class CommentCreate(BaseModel):
    content : str


class CommentResponse(BaseModel):
    id : int
    task_id : int
    user_id : int
    content : str
    created_at : datetime

    model_config = {
        'from_attributes' : True,
    }

