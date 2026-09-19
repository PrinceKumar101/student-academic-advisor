from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    code: str
    message: str


class ImportResultOut(BaseModel):
    kind: str
    dry_run: bool
    valid: bool
    committed: bool
    created_count: int
    errors: list[ImportRowError]
