from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User   # correct model
from models.project import Project
from apis.schemas.user import UserCreate, UserUpdate, UserGet
import datetime
from typing import Optional

router = APIRouter()


# CREATE USER
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        # Use HTTPException so the frontend 'catch' block triggers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ID is already registered"
        )

    if user.mobile:
        existing_mobile = db.query(User).filter(User.mobile == user.mobile).first()
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )
        
    new_user = User(**user.model_dump())
    new_user.organisation = user.email.split('@')[-1]
    new_user.created_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"User created successfully": new_user}


@router.post("/valid")
def validate_user(getuser: UserGet, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == getuser.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if getuser.password != user.password:
        raise HTTPException(status_code=404, detail="Please check your password")

    return user


@router.get("/project/{project_id}")
def get_users_by_project(project_id: int, db: Session = Depends(get_db), ):
    return db.query(User).join(User.projects).filter(Project.id == project_id).all()


@router.get("/assignproject/{organisation}")  
def get_users_not_in_project(organisation: str, project_id: int, db: Session = Depends(get_db), ):
    
        return (
        db.query(User)
        .filter(
            User.organisation == organisation,
            # This selects users who DO NOT have a project with this ID
            ~User.projects.any(Project.id == project_id)
        )
        .all()
    )
   
@router.get("/unassignproject/{organisation}")  
def get_users_in_project(organisation: str, project_id: int, db: Session = Depends(get_db), ):
    
       return (
        db.query(User)
        .join(User.projects) # Connects the User table to the Projects table
        .filter(
            User.organisation == organisation,
            Project.id == project_id # Filters for specifically this project
        )
        .all()
    )

# GET USER BY ID
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# UPDATE USER
@router.patch("/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db_user.updated_at =  datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE USER
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}