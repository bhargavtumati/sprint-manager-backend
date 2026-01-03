from pydantic import BaseModel

from enum import Enum

class WorkType(str, Enum):
    BUG = "Bug"
    TASK = "Task"
    STORY = "Story"
    REVIEW = "Review"

class Workflow(str, Enum):
    BACKLOG = "Backlog"
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    DONE = "Done"

class Priority(str, Enum):
    BLOCKER = "Blocker"
    CRITICAL = "Critical"
    MAJOR = "Major"
    MEDIUM = "Medium"
    MINOR = "Minor"
    TRIVIAL = "Trivial"


class TaskCreate(BaseModel):
 
    title: str
    work_type: WorkType
    work_flow: Workflow
    sprint_id: int | None = None
    project_id: int
    priority: Priority
    story_points: int | None = None
    user_id: int | None = None
    description: str | None = None
    parent_task: int | None = None



class TaskUpdate(BaseModel):

    title: str | None = None
    work_type: WorkType | None = None
    work_flow: Workflow | None = None
    story_points: int | None = None
    user_id: int | None = None
    description: str | None = None
    parent_task: int | None = None
    sprint_id: int | None = None
    project_id: int | None = None
    priority: Priority | None = None

    # validators/task.py
from fastapi import HTTPException, status

def validate_search_query(q: str) -> str:
    search_text = q.strip()

    if not search_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )

    if len(search_text) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query is too long"
        )

    return search_text
