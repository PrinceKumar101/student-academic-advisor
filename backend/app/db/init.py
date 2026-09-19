from sqlalchemy.engine import Engine

from app.db.base import Base


def create_all(bind: Engine | None = None) -> None:
    """Create tables for imported models. Import identity models so they register."""
    from app import models  # noqa: F401
    from app.db.session import engine as app_engine

    Base.metadata.create_all(bind=bind or app_engine)
