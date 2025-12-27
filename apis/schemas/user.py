from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    full_name: str | None = None
    email: str
    password: str
    mobile: str | None = None
    role: str | None = None
    location: str | None = None
    organisation: str | None = None
  

    @field_validator("mobile")
    def validate_mobile(cls, value):
        if value is None:
            return value
        elif not value.isdigit():
            raise ValueError("Mobile number must contain only digits")
        elif len(value) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return value
    
    @field_validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Email must contain '@'")
        elif "." not in value.split("@")[-1]:
            raise ValueError("Email must contain '.' after '@'")
        return value
    

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    mobile: str | None = None
    role: str | None = None
    location: str | None = None
    organisation: str | None = None


class UserGet(BaseModel): 
    email: str
    password: str

class AssignProjects(BaseModel):
    project_ids: list[int]
    


