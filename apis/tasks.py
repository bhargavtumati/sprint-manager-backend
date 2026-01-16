from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from apis.schemas.ai import PromptRequest 
from typing import Optional
from fastapi import Query

from apis.ai import send_task_to_gemini
from apis.schemas.task import TaskCreate, TaskUpdate
from apis.schemas.task import validate_search_query


router = APIRouter()


NO_DESCRIPTION_GENERATED = "No description generated"
TASK_NOT_FOUND = "Task not found"

@router.post("/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):\

    # Find last code
    last_task = db.query(Task).order_by(Task.code.desc()).first()
    new_code = int(last_task.code) + 1 if last_task else 1001

    # Create Task instance with code
    new_task = Task(
        work_type=task.work_type,
        title=task.title,
        work_flow=task.work_flow,
        story_points=task.story_points,
        priority=task.priority,
        user_id=task.user_id,
        parent_task=task.parent_task,
        sprint_id=task.sprint_id,
        project_id=task.project_id,
        description=task.description,
        code=new_code  

    )
    if not new_task.description:
        try:
            prompt=f"generate a description on how to do the {new_task.title } task in our project in points, make sure length of description is not more than 1000 characters"
            request = PromptRequest(prompt=prompt)
            result = send_task_to_gemini(request)
            new_task.description = result.get("result", NO_DESCRIPTION_GENERATED)
       
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Error generating description: {str(e)}")

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        "task": new_task
       
    }

@router.get("/all/{project_id}")
def get_all_tasks(
    project_id: int, 
    sprint_id: Optional[int] = None, 
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.project_id == project_id)

    if sprint_id is not None:
        query = query.filter(Task.sprint_id == sprint_id)
    
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)

    return query.all()


@router.get("/unassigned/{project_id}")
def get_unassigned_tasks(
    project_id: int, 
    user_id: Optional[int] = None, 
    sprint_id: Optional[int] = None, 
    backlog: Optional[bool]= False,
    db: Session = Depends(get_db)
):
    # Base query: must match project and must be unassigned (sprint_id is NULL)
    query = db.query(Task).filter(
        Task.project_id == project_id 
    )
    # Optional: filter by a specific sprint if provided
    # If user_id, it will return ALL assigned tasks in the project for that user where sprint_id is null
    if user_id is not None:
        query = query.filter(Task.user_id == user_id, Task.sprint_id.is_(None))
         
    elif sprint_id is not None:
        query = query.filter(Task.sprint_id == sprint_id, Task.user_id.is_(None))

    elif backlog:
        query = query.filter(Task.user_id.is_(None), Task.sprint_id.is_(None))

    return query.all()


# GET TASK BY ID
@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    return task


# UPDATE TASK
@router.patch("/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)
    
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    if not db_task.description:
        try:
            prompt=f"generate a description on how to do the {db_task.title } task in our project in points, make sure length of description is not more than 1000 characters"
            request = PromptRequest(prompt=prompt)
            result = send_task_to_gemini(request)
            db_task.description = result.get("result", NO_DESCRIPTION_GENERATED)
       
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Error generating description: {str(e)}")

    db.commit()
    db.refresh(db_task)
    return db_task



# UPDATE DESCRIPTION
@router.patch("/{task_id}/description")
def update_description(task_id: int, req: PromptRequest, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    try:
        prompt=req.prompt
        request = PromptRequest(prompt=prompt)
        result = send_task_to_gemini(request)
        description = result.get("result", NO_DESCRIPTION_GENERATED)
       
    except Exception as e:
        description = f"Error generating description: {str(e)}"

    # Update the task
    db_task.description = description
    db.commit()
    db.refresh(db_task)

    return db_task



# DELETE TASK
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}



# 🔍 SEARCH TASKS
@router.get("/search/ByTitle")
def search_tasks(
    q: str = Query(..., description="Task title"),
    db: Session = Depends(get_db)
):
    search_text = validate_search_query(q)  # ✅ validation used here

    tasks = (
        db.query(Task)
        .filter(Task.title.ilike(f"%{search_text}%"))
        .all()
    )
    if len(tasks):
        return tasks
    else:
        return "No task is found with your search!"