from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from apis.schemas.project import ProjectCreate, ProjectUpdate
from models.user import User

router = APIRouter()


# CREATE PROJECT
@router.post("/")
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    # 1. Fetch existing User objects from the DB using the IDs provided
    # project_data.users is a list of ints like [1, 2, 3]
    users_to_add = db.query(User).filter(User.id.in_(project_data.users)).all()

    # 2. Create the Project instance
    new_project = Project(title=project_data.title)

    # 3. Establish the relationship
    # This automatically creates entries in the 'user_projects' table
    new_project.users = users_to_add

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project

# Get all projects
@router.get("/user/{user_id}")
def get_projects_by_user(user_id: int, db: Session = Depends(get_db), ):
    return db.query(Project).join(Project.users).filter(User.id == user_id).all()

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
