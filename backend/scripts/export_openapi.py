"""Write the FastAPI OpenAPI document to the repo root."""

from __future__ import annotations

import json
from pathlib import Path

from app.main import create_app

ROOT = Path(__file__).resolve().parents[2]


def export_openapi(path: Path | None = None) -> Path:
    target = path or (ROOT / "openapi.json")
    spec = create_app().openapi()
    target.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> None:
    written = export_openapi()
    print(f"Wrote {written}")


if __name__ == "__main__":
    main()
