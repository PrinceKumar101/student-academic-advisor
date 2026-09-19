from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttendanceRecordCreate(BaseModel):
    student_id: int
    subject_id: int
    record_date: date
    classes_held: int = Field(ge=0)
    classes_attended: int = Field(ge=0)

    @model_validator(mode="after")
    def attended_within_held(self) -> "AttendanceRecordCreate":
        if self.classes_attended > self.classes_held:
            raise ValueError("classes_attended cannot exceed classes_held")
        return self


class AttendanceRecordUpdate(BaseModel):
    record_date: date | None = None
    classes_held: int | None = Field(default=None, ge=0)
    classes_attended: int | None = Field(default=None, ge=0)


class AttendanceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    subject_id: int
    record_date: date
    classes_held: int
    classes_attended: int


class AttendanceSummaryOut(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    classes_held: int
    classes_attended: int
    attendance_percent: float | None


class AttendanceListOut(BaseModel):
    student_id: int
    summaries: list[AttendanceSummaryOut]
    records: list[AttendanceRecordOut]
