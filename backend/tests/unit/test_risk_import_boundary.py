import ast
from pathlib import Path

ENGINES = Path(__file__).resolve().parents[2] / "app" / "engines"
FORBIDDEN_PREFIXES = ("fastapi", "sqlalchemy", "app.ai", "ai")


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_engines_have_no_framework_or_ai_imports() -> None:
    files = list(ENGINES.glob("*.py"))
    assert files
    for path in files:
        source = path.read_text()
        assert "datetime.now" not in source
        for module in _imported_modules(path):
            assert not any(
                module == prefix or module.startswith(prefix + ".")
                for prefix in FORBIDDEN_PREFIXES
            ), f"{path.name} imports {module}"
