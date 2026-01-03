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
@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

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


@router.get("/user/{user_id}")
def get_all_task_for_user_sprint(user_id:int,db:Session=Depends(get_db)):
    sprint=db.query(Sprint).filter(Sprint.status==True).first()
    if not sprint:
        return []
    task=[]
    task=db.query(Task).filter(Task.user_id==user_id).all()

    return  task 



# UPDATE TASK
@router.patch("/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()

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
@router.patch("/{task_id}/description")
def update_description(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
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
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}
#get the task based on title
@router.get("/byTitle/search")
def search_tasks(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)):
    search_text=validate_search_query
    tasks = (
        db.query(Task)
        .filter(Task.title.ilike(f"%{search_text}%"))  # 🔥 case-insensitive
        .all()
    )
    return tasks if len(tasks) > 0 else {"message": "No task found with your search"}







