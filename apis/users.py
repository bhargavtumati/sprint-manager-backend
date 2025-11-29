from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User   # correct model
from apis.schemas.user import UserCreate, UserUpdate, UserGet

router = APIRouter()


# CREATE USER
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        return { "Email id is already registered"}

    if user.mobile:
        existing_mobile = db.query(User).filter(User.mobile == user.mobile).first()
        if existing_mobile:
            return {"error": "Mobile number already registered"}

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"User created successfully": new_user}




# GET USER BY ID
@router.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post("/valid")
def get_user(getuser: UserGet, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == getuser.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if getuser.password != user.password:
        raise HTTPException(status_code=404, detail="Please check your password")

    return user


# UPDATE USER
@router.put("/{id}")
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE USER
@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


