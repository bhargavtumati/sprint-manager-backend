from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_

from database import get_db
from models.task import Task
from apis.schemas.search_bar import SearchTaskRequest

router = APIRouter()

@router.post("/")
def search_tasks(payload: SearchTaskRequest, db: Session = Depends(get_db)):
    value = payload.search_bar.strip()

    # If numeric → search by code
    if value.isdigit():
        tasks = (
            db.query(Task)
            .filter(Task.code == int(value))
            .all()
        )
    else:
        # Search by title
        tasks = (
            db.query(Task)
            .filter(Task.title.ilike(f"%{value}%"))
            .all()
        )
    if not tasks:
        raise HTTPException(
            status_code=400,
            detail="We couldn't find any results with that title"
        )

    return tasks
        
        
    
