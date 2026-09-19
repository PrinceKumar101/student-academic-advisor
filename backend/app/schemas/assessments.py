from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import AssessmentStatus, AssessmentType


class AssessmentCreate(BaseModel):
    student_id: int
    subject_id: int
    type: AssessmentType
    name: str = Field(min_length=1, max_length=255)
    max_marks: float = Field(gt=0)
    obtained_marks: float | None = Field(default=None, ge=0)
    status: AssessmentStatus
    assessment_date: date

    @model_validator(mode="after")
    def marks_rules(self) -> "AssessmentCreate":
        if self.obtained_marks is not None and self.obtained_marks > self.max_marks:
            raise ValueError("obtained_marks cannot exceed max_marks")
        if self.status == AssessmentStatus.GRADED and self.obtained_marks is None:
            raise ValueError("GRADED assessments require obtained_marks")
        return self


class AssessmentUpdate(BaseModel):
    type: AssessmentType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    max_marks: float | None = Field(default=None, gt=0)
    obtained_marks: float | None = Field(default=None, ge=0)
    status: AssessmentStatus | None = None
    assessment_date: date | None = None


class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    subject_id: int
    type: AssessmentType
    name: str
    max_marks: float
    obtained_marks: float | None
    status: AssessmentStatus
    assessment_date: date
