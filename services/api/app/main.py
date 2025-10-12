from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.admin import router as admin_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.attempts import router as attempts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.subjects import router as subjects_router
from app.api.routes.health import router as health_router
from app.api.routes.bookmarks import router as bookmarks_router
from app.api.routes.practice import router as practice_router
from app.api.routes.questions import router as questions_router
from app.api.routes.quizzes import router as quizzes_router
from app.api.routes.users import router as users_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.organizations import router as organizations_router

app = FastAPI(title="Loksewa Quiz Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(quizzes_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(subjects_router, prefix="/api")
app.include_router(practice_router, prefix="/api")
app.include_router(attempts_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(bookmarks_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(organizations_router, prefix="/api")
