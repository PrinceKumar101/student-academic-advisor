from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    ai,
    analytics,
    assessments,
    attendance,
    auth,
    health,
    imports,
    interventions,
    risk,
    students,
    study_plans,
    subjects,
    teacher,
    trends,
)
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import RequestIdMiddleware, configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(title="Student Academic Advisor", version="1.0.0")
    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(students.router, prefix="/api/v1")
    app.include_router(subjects.router, prefix="/api/v1")
    app.include_router(attendance.router, prefix="/api/v1")
    app.include_router(assessments.router, prefix="/api/v1")
    app.include_router(risk.router, prefix="/api/v1")
    app.include_router(trends.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(ai.router, prefix="/api/v1")
    app.include_router(study_plans.router, prefix="/api/v1")
    app.include_router(interventions.router, prefix="/api/v1")
    app.include_router(teacher.router, prefix="/api/v1")
    app.include_router(imports.router, prefix="/api/v1")
    return app


app = create_app()
