from typing import Optional, Annotated

from pydantic import BaseModel, Field, field_validator

from citizen_connect_app.models.utils import Location, Category


class CommunityCheck(BaseModel):
    user_id: Optional[str] = None

    category: Optional[Category] = None
    location: Optional[Location] = None

    water_supply: Optional[str] = None
    electricity: Optional[str] = None
    road: Optional[str] = None
    teacher_at_school: Optional[str] = None
    healthcare: Optional[str] = None
    internet: Optional[str] = None
    sanitation: Optional[str] = None
    local_governance: Optional[str] = None

    additional_observations: Optional[
        Annotated[str, Field(max_length=3000)]
    ] = None

    media: Optional[str] = None

    confidence_level: str
    files: list = Field(default_factory=list)

    @field_validator("additional_observations", mode="before")
    @classmethod
    def clean_observations(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, value):
        return None if value == "" else value


