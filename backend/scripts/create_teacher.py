"""Create a TEACHER user and profile. Public register cannot set this role."""

from __future__ import annotations

import argparse
import sys

from app.core.config import get_settings
from app.core.errors import Conflict
from app.db.session import SessionLocal
from app.services.auth_service import create_teacher_account


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a teacher account.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--full-name", required=True, dest="full_name")
    parser.add_argument("--department", required=True)
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        raise SystemExit(1)

    settings = get_settings()
    print(f"Using {settings.database_url}")
    session = SessionLocal()
    try:
        teacher = create_teacher_account(
            session,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            department=args.department,
        )
        teacher_id = teacher.id
        email = args.email.strip().lower()
    except Conflict as exc:
        print(exc.message, file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        session.close()

    print(f"Created teacher id={teacher_id} email={email}")


if __name__ == "__main__":
    main()
