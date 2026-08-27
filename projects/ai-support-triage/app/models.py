from enum import StrEnum
from pydantic import BaseModel, Field


class Category(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Ticket(BaseModel):
    subject: str = Field(min_length=3, max_length=160)
    message: str = Field(min_length=5, max_length=4000)


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    confidence: float = Field(ge=0, le=1)
    signals: list[str]
    suggested_action: str
