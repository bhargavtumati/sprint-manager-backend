from sqlalchemy import Column, Integer, String
from database import Base



class User(Base):
    __tablename__="user"

    id=Column(Integer,primary_key=True,index=True)
    full_name=Column(String,index=True,nullable=True)
    email=Column(String,index=True,nullable=False, unique=True)
    password=Column(String,nullable=False)
    mobile = Column(String, nullable=True, unique=True)
    role=Column(String,index=True, nullable=True)
    location=Column(String,index=True, nullable=True)
    organisation=Column(String,index=True, nullable=True)