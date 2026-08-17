from typing import Optional, Annotated

from pydantic import BaseModel, Field, field_validator

from citizen_connect_app.models.utils import Location, Category


class Issue(BaseModel):
    user_id: Optional[str] = None

    description: Annotated[str, Field(min_length=10, max_length=3000)]
    urgency: str
    allow_contact: bool = False

    location: Optional[Location] = None
    category: Optional[Category] = None

    files: list = Field(default_factory=list)
    
    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str):
        return value.strip()

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, value):
        return None if value == "" else value