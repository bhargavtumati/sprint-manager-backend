from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean
from database import Base



class Sprint(Base):
    __tablename__="sprint"
    id=Column(Integer,primary_key=True,index=True)
    start_date=Column(Date,nullable=True)
    end_date=Column(Date,nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)