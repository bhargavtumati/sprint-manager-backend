from pydantic import BaseModel
from datetime import datetime

class SprintCreate(BaseModel):
    
    start_date: datetime
    end_date: datetime
    project_id: int


class SprintUpdate(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    project_id: int
