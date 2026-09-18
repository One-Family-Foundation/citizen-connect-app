from datetime import date
from typing import Optional, Annotated

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
)

from citizen_connect_app.models.utils import (
    Location,
    Category,
    CategoryResponse, LocationResponse, MediaResponse,
   
)
from citizen_connect_app.models.user import UserSummary

class VolunteerAction(BaseModel):
    description: Annotated[
        str,
        Field(min_length=10, max_length=3000)
    ]

    location: Optional[Location] = None

    category: Category

    media: list = Field(default_factory=list)

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value):
        if value is None:
            return value

        return value.strip()

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, value):
        return None if value == "" else value

    @model_validator(mode="after")
    def validate_category(self):
        if not self.category.l1:
            raise ValueError("category.l1 is required")

        if not self.category.l2:
            raise ValueError("category.l2 is required")

        return self

class VolunteerActionResponse(BaseModel):
    id:str
    user:UserSummary | None = None
    description:str
    category: CategoryResponse
    location: LocationResponse | None = None
    media: list[MediaResponse]=[]
    start_date: date | None = None
    end_date: date | None = None