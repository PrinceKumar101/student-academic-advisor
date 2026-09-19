import ast
from pathlib import Path

AI = Path(__file__).resolve().parents[2] / "app" / "ai"
FORBIDDEN_PREFIXES = ("app.models", "fastapi", "sqlalchemy")


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_ai_package_does_not_import_models_or_frameworks() -> None:
    files = [path for path in AI.rglob("*.py") if path.name != "__pycache__"]
    assert files
    for path in files:
        for module in _imported_modules(path):
            assert not any(
                module == prefix or module.startswith(prefix + ".")
                for prefix in FORBIDDEN_PREFIXES
            ), f"{path.name} imports {module}"
