from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from apis.schemas.project import ProjectCreate, ProjectUpdate

router = APIRouter()


# CREATE PROJECT
@router.post("/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# GET PROJECT
@router.get("/{id}")
def get_project(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


# UPDATE PROJECT
@router.put("/{id}")
def update_project(id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == id).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project


# DELETE PROJECT
@router.delete("/{id}")
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}
