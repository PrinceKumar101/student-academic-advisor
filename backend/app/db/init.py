from sqlalchemy.engine import Engine

from app.db.base import Base


def _bind(bind: Engine | None) -> Engine:
    from app.db.session import engine as app_engine

    return bind or app_engine


def create_all(bind: Engine | None = None) -> None:
    """Create tables for imported models. Import models so they register."""
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=_bind(bind))


def drop_all(bind: Engine | None = None) -> None:
    """Drop all registered tables."""
    from app import models  # noqa: F401

    Base.metadata.drop_all(bind=_bind(bind))
