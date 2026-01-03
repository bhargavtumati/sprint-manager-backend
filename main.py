from fastapi import FastAPI
from database import Base, engine
from apis.tasks import router as task_router
from apis.projects import router as project_router
from apis.users import router as user_router
from apis.sprints import router as sprint_router
from apis.search_bar import router as search_router
from fastapi.middleware.cors import CORSMiddleware
from apis.ai import router as ai_router





app = FastAPI(
    title="Sprint Manager API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React / Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create PostgreSQL tables
Base.metadata.create_all(bind=engine)


# Include API Routes
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(project_router, prefix="/projects", tags=["Projects"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(sprint_router, prefix="/sprints", tags=["Sprints"])
app.include_router(ai_router,prefix="/ai",tags=["Ai"])
app.include_router(search_router,prefix="/search_bar",tags=["Search"])
