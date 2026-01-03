from sqlalchemy import Column, Integer, ForeignKey
from database import Base


class SearchTask(Base):
    __tablename__ = "search_bar"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=True)
