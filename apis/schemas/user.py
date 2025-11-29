from pydantic import BaseModel

class UserCreate(BaseModel):
    full_name: str | None = None
    email: str
    password: str
    mobile: int | None = None
    role: str | None = None
    location: str | None = None
    organisation: str | None = None
    

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    mobile: int | None = None
    role: str | None = None
    location: str | None = None
    organisation: str | None = None

class UserGet(BaseModel): 
    email: str
    password: str
    
