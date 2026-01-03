from pydantic import BaseModel, Field

class SearchTaskRequest(BaseModel):
    search_bar: str = Field(
        ...,
        min_length=1,  # allow single-digit codes
        max_length=100,
        description="Search by task title or task code"
    )
