from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    semester: int = Field(ge=1, le=8)


class SubjectUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    semester: int | None = Field(default=None, ge=1, le=8)


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    semester: int


class EnrollmentCreate(BaseModel):
    student_id: int


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    subject_id: int
