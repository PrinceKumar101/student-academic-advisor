from collections.abc import Generator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import authorize_student_access, require_role
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.init import create_all
from app.db.session import get_db, make_engine
from app.main import create_app
from app.models.enums import UserRole
from app.models.student import Student
from app.models.user import User


@pytest.fixture
def app() -> FastAPI:
    get_settings.cache_clear()
    application = create_app()

    class EchoBody(BaseModel):
        name: str

    @application.post("/api/v1/_test/echo")
    def echo(body: EchoBody) -> EchoBody:
        return body

    @application.get("/api/v1/_test/boom")
    def boom() -> None:
        raise RuntimeError("forced failure")

    return application


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def db_engine() -> Generator[Engine, None, None]:
    engine = make_engine("sqlite:///:memory:")
    create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def demo_password_hash() -> str:
    return hash_password("Demo@1234")


@pytest.fixture
def auth_app(db_session: Session) -> FastAPI:
    get_settings.cache_clear()
    application = create_app()

    def override_db() -> Generator[Session, None, None]:
        yield db_session

    application.dependency_overrides[get_db] = override_db

    @application.get("/api/v1/_test/teacher-only")
    def teacher_only(
        user: User = Depends(require_role(UserRole.TEACHER)),
    ) -> dict[str, int]:
        return {"user_id": user.id}

    @application.get("/api/v1/_test/students/{student_id}")
    def student_peek(
        student: Student = Depends(authorize_student_access),
    ) -> dict[str, int]:
        return {"student_id": student.id}

    return application


@pytest.fixture
def auth_client(auth_app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(auth_app, raise_server_exceptions=False) as test_client:
        yield test_client
