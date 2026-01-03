from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.sprint import Sprint
from apis.schemas.ai import PromptRequest 

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


# GET TASK BY ID
@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    return task


@router.get("/sprint/{sprint_id}")
def get_all_tasks_for_sprint_id(sprint_id: int, db:Session=Depends(get_db)):
    
    sprint=db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
         raise HTTPException(status_code=404, detail="Sprint not found")
    tasks=[]
    tasks=db.query(Task).filter(Task.sprint_id==sprint.id).all()
    
    return  tasks 


@router.get("/unassigned/{project_id}")
def get_all_tasks_for_project_id(project_id: int, db:Session=Depends(get_db)):
    
    tasks=[]

    tasks=db.query(Task).filter(Task.project_id==project_id, Task.sprint_id==None).all()
    
    return  tasks 


@router.get("/{sprint_id}/user/{user_id}")
def get_all_task_for_user_sprint(user_id:int, sprint_id:int, db:Session=Depends(get_db)):
    sprint=db.query(Sprint).filter(Sprint.id==sprint_id).first()
    if not sprint:
        return []
    tasks=[]
    tasks=db.query(Task).filter(Task.user_id==user_id, Task.sprint_id==sprint.id).all()

    return  tasks 


@router.get("/user/{user_id}")
def get_all_task_for_user_backlog(user_id:int,  db:Session=Depends(get_db)):
    
    tasks=[]
    tasks=db.query(Task).filter(Task.user_id==user_id, Task.sprint_id==None).all()

    return  tasks 


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
            prompt=f"generate a description specifying the points in general {db_task.title}"
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



