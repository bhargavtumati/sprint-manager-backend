from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.sprint import Sprint
from apis.schemas.ai import PromptRequest 

from apis.ai import send_task_to_gemini
from apis.schemas.task import TaskCreate, TaskUpdate


router = APIRouter()




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
            prompt=f"generate a description on how to the task in our project in points,make sure length of description is not more than 1000 characters{new_task.title }"
            request = PromptRequest(prompt=prompt)
            result = send_task_to_gemini(request)
            new_task.description = result.get("result", "No description generated")
       
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Error generating description: {str(e)}")

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    

    return {
        "task": new_task
       
    }



# GET TASK BY ID
@router.get("/{id}")
def get_task(id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.get("/")
def get_all_tasks_sprint(db:Session=Depends(get_db)):
    
    sprint=db.query(Sprint).filter(Sprint.status==True).first()
    if not sprint:
        return []
    tasks=db.query(Task).filter(Task.sprint_id==sprint.id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")
    return  tasks 

@router.get("/{id}")
def get_all_task_user_sprint(id:int,db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==id),
    sprint=db.query(Sprint).filter(Sprint.id==id)
    if not Task and Sprint:
        raise HTTPException(status_code=404, detail="Task not found")

    return  task ,sprint

@router.get("/{user_id}")
def filter_tasks_per_sprint(user_id:int,db:Session=Depends(get_db)):

    tasks=db.query(Task).filter(Task.user_id==user_id).all()
    
    if not Task:
        raise HTTPException(status_code=404, detail="Task not found")

    return  tasks

# UPDATE TASK
@router.patch("/{id}")
def update_task(id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    if not db_task.description:
        try:
            prompt=f"generate a description specifying the points in general {db_task.title}"
            request = PromptRequest(prompt=prompt)
            result = send_task_to_gemini(request)
            db_task.description = result.get("result", "No description generated")
       
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Error generating description: {str(e)}")

    db.commit()
    db.refresh(db_task)
    return db_task


# UPDATE DESCRIPTION
@router.patch("/{id}/description")
def update_description(id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        prompt=f"generate a description specifying the points in general {db_task.title}"
        request = PromptRequest(prompt=prompt)
        result = send_task_to_gemini(request)
        description = result.get("result", "No description generated")
       
    except Exception as e:
        description = f"Error generating description: {str(e)}"

    # Update the task
    db_task.description = description
    db.commit()
    db.refresh(db_task)

    return db_task


# DELETE TASK
@router.delete("/{id}")
def delete_task(id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}



