from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.init import create_all
from app.db.session import make_engine
from app.main import create_app


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
