from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sprint import Sprint
from apis.schemas.sprint import SprintCreate, SprintUpdate

router = APIRouter()


# CREATE SPRINT
@router.post("/")
def create_sprint(sprint: SprintCreate, db: Session = Depends(get_db)):
    new_sprint = Sprint(**sprint.model_dump())
    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)
    return new_sprint


# GET SPRINT BY ID
@router.get("/{id}")
def get_sprint(id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == id).first()

    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    return sprint


# UPDATE SPRINT
@router.put("/{id}")
def update_sprint(id: int, sprint: SprintUpdate, db: Session = Depends(get_db)):
    db_sprint = db.query(Sprint).filter(Sprint.id == id).first()

    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    for key, value in sprint.model_dump(exclude_unset=True).items():
        setattr(db_sprint, key, value)

    db.commit()
    db.refresh(db_sprint)
    return db_sprint


# DELETE SPRINT
@router.delete("/{id}")
def delete_sprint(id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == id).first()

    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    db.delete(sprint)
    db.commit()
    return {"message": "Sprint deleted successfully"}
