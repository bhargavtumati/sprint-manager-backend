from sqlalchemy import Column, Integer, String
from database import Base


class Project(Base):
    __tablename__="project"
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,index=True)








