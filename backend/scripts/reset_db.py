"""Drop and recreate all tables. Seed is a separate command (`seed_demo`)."""

from __future__ import annotations

import argparse

from app.core.config import get_settings
from app.db.init import create_all, drop_all
from app.db.session import engine


def reset_database() -> None:
    drop_all(engine)
    create_all(engine)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Drop and recreate the database schema (no seed data)."
    )
    parser.parse_args()
    settings = get_settings()
    print(f"Resetting schema at {settings.database_url}")
    reset_database()
    print("Schema recreated.")


if __name__ == "__main__":
    main()
