from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class AssessmentType(StrEnum):
    INTERNAL = "INTERNAL"
    QUIZ = "QUIZ"
    ASSIGNMENT = "ASSIGNMENT"
    EXAM = "EXAM"


class AssessmentStatus(StrEnum):
    GRADED = "GRADED"
    MISSING = "MISSING"
    PENDING = "PENDING"


class Priority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InterventionStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TrendLabel(StrEnum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SuddenChange(StrEnum):
    SUDDEN_RISE = "SUDDEN_RISE"
    SUDDEN_DROP = "SUDDEN_DROP"


class Source(StrEnum):
    AI = "AI"
    FALLBACK = "FALLBACK"


class ChatMessageRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class SubjectBand(StrEnum):
    HIGH_CONCERN = "HIGH_CONCERN"
    MEDIUM = "MEDIUM"
    GOOD = "GOOD"


class WarningSeverity(StrEnum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ProgressDirection(StrEnum):
    IMPROVED = "IMPROVED"
    WORSENED = "WORSENED"
    UNCHANGED = "UNCHANGED"


class FallbackReason(StrEnum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    TIMEOUT = "TIMEOUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    UNGROUNDED_OUTPUT = "UNGROUNDED_OUTPUT"


class AdviceKind(StrEnum):
    ANALYSIS = "ANALYSIS"
