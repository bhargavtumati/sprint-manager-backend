from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sprint import Sprint
from models.project import Project


from apis.schemas.sprint import SprintCreate, SprintUpdate

router = APIRouter()

SPRINT_NOT_FOUND = "Sprint not found"
# CREATE SPRINT

@router.post("/")
def create_sprint(sprint: SprintCreate, db: Session = Depends(get_db)):

    # Validate project
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="Invalid project_id"
        )

    #  Validate dates
    if sprint.end_date <= sprint.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    # Prevent overlapping sprints
    existing_sprint = db.query(Sprint).filter(
        Sprint.project_id == sprint.project_id,
        Sprint.start_date <= sprint.end_date,
        Sprint.end_date >= sprint.start_date
    ).first()

    if existing_sprint:
        raise HTTPException(
            status_code=400,
            detail="Sprint already exists or overlaps with another sprint"
        )

    # Create sprint
    new_sprint = Sprint(**sprint.model_dump())
    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)

    return new_sprint



# GET SPRINT BY ID
@router.get("/{sprint_id}/fetch")
def get_sprint(sprint_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)

    return sprint

# Get all sprints
@router.get("/{project_id}")
def get_all_sprint(project_id: int, db: Session = Depends(get_db)):
    return db.query(Sprint).filter(Sprint.project_id == project_id).all()


# UPDATE SPRINT
@router.put("/{sprint_id}")
def update_sprint(sprint_id: int, sprint: SprintUpdate, db: Session = Depends(get_db)):
    db_sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    for key, value in sprint.model_dump(exclude_unset=True).items():
        setattr(db_sprint, key, value)

    db.commit()
    db.refresh(db_sprint)
    return db_sprint

@router.patch("/{sprint_id}")
def end_sprint(sprint_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
    
    sprint.status = False
    sprint.end_date = date.today()
    db.commit()
    return {"message": "Sprint ended successfully"}

# DELETE SPRINT
@router.delete("/{sprint_id}")
def delete_sprint(sprint_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)

    db.delete(sprint)
    db.commit()
    return {"message": "Sprint deleted successfully"}
