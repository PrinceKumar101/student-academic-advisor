from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole

LOGIN_FAILURE_MESSAGE = "Invalid email or password"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    student_code: str = Field(min_length=1, max_length=64)
    department: str = Field(min_length=1, max_length=128)
    semester: int = Field(ge=1, le=8)
    section: str = Field(min_length=1, max_length=16)


class RegisterResponse(BaseModel):
    user_id: int
    student_id: int


class AuthUserOut(BaseModel):
    id: int
    role: UserRole
    student_id: int | None = None
    teacher_id: int | None = None
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserOut


class MeResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    student_id: int | None = None
    teacher_id: int | None = None
    full_name: str
