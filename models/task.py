from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey
from database import Base



WorkType = ('Bug', 'Task', 'Story', 'Review')
Workflow = ('Backlog', 'To Do', 'In Progress', 'On Hold', 'Done')
Priority = ('Blocker', 'Critical', 'Major','Medium', 'Minor', 'Trivial')



class Task(Base):
    __tablename__ = "task"
   # __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, index=True)

    work_type = Column(Enum(*WorkType, name="work_type_enum"), nullable=False)
    code = Column(Integer, index=True,  unique=True,nullable=False)
    title = Column(String, index=True, nullable=False)
    work_flow = Column(Enum(*Workflow, name="workflow_enum"), nullable=True)
    story_points = Column(Integer, nullable=True)
    priority = Column(Enum(*Priority, name="status_enum"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    parent_task =   Column(Integer, ForeignKey("task.id"), nullable=True)

    sprint_id = Column(Integer, ForeignKey ("sprint.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    description = Column(Text, nullable=True)
