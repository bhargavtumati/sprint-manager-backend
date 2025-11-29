from pydantic import BaseModel

class ProjectCreate(BaseModel):
    title: str
    

class ProjectUpdate(BaseModel):
    title: str | None = None
    
