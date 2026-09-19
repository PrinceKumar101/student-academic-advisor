"""Load the deterministic demo dataset. Run after `python -m scripts.reset_db`."""

from __future__ import annotations

import argparse
from datetime import date

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from scripts.seed_generator import DEFAULT_AS_OF, seed_demo


def _parse_as_of(value: str) -> date:
    return date.fromisoformat(value)


def run_seed(session: Session, as_of: date) -> None:
    result = seed_demo(session, as_of=as_of)
    session.commit()
    count = len(result.profiles_by_email)
    print(f"Seeded {count} students as of {result.as_of.isoformat()}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the demo academic dataset.")
    parser.add_argument(
        "--as-of",
        dest="as_of",
        type=_parse_as_of,
        default=DEFAULT_AS_OF,
        help=(
            "Inclusive end date for weekly records "
            f"(default {DEFAULT_AS_OF.isoformat()})."
        ),
    )
    args = parser.parse_args()
    settings = get_settings()
    print(f"Seeding {settings.database_url}")
    session = SessionLocal()
    try:
        run_seed(session, args.as_of)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
