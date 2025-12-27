from pydantic import BaseModel

from models.user import User
from apis.schemas.user import UserCreate

class ProjectCreate(BaseModel):
    title: str
    users: list[int]
    

class ProjectUpdate(BaseModel):
    title: str | None = None
    
