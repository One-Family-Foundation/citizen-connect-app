from typing import Optional, Annotated

from pydantic import BaseModel, Field, field_validator

from citizen_connect_app.models.utils import Location, Category


class ReportIssue(BaseModel):
    user_id: Optional[str] = None

    description: Annotated[str, Field(min_length=10, max_length=3000)]
    urgency: str
    allow_contact: bool = False

    location: Optional[Location] = None
    category: Optional[Category] = None

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str):
        return value.strip()

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, value):
        return None if value == "" else value


class ReportIssueResponse(BaseModel):
    id: str
    description: str
    urgency: str
    allow_contact: bool

    country: Optional[str] = None
    geography_l1: Optional[str] = None
    geography_l2: Optional[str] = None

    category_l1: Optional[str] = None
    category_l2: Optional[str] = None

    user_id: Optional[str] = None

    media: Optional[str] = None

    creation: str
    modified: str