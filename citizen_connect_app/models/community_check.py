from typing import Optional, Annotated

from pydantic import BaseModel, Field, field_validator

from citizen_connect_app.models.utils import Location


class CommunityCheck(BaseModel):
    user_id: Optional[str] = None

    location: Optional[Location] = None

    title: Optional[str] = None

    description: Optional[
        Annotated[str, Field(max_length=3000)]
    ] = None
    category:Optional[str]=None

    water_supply: str
    electricity: str
    road: str
    teacher_at_school: str
    healthcare: str
    internet:str
    sanitation: str
    local_governance: str

    confidence_level: str

    files: list = Field(default_factory=list)

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("location", mode="before")
    @classmethod
    def clean_location(cls, value):
        return None if value == "" else value