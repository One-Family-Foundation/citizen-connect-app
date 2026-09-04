from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from citizen_connect_app.models.utils import Location, Category, MediaResponse, LocationResponse, CategoryResponse
from citizen_connect_app.models.user import UserSummary

class Post(BaseModel):
    description: Annotated[str, Field(min_length=10, max_length=3000)]
    location: Optional[Location] = None
    category : Category
    files: list = Field(default_factory=list)

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str):
        return value.strip()

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, value):
        return None if value == "" else value

class PostResponse(BaseModel):
    id: str
    description: str
    location: LocationResponse | None = None
    category: CategoryResponse | None = None
    user: UserSummary

    media: list[MediaResponse] = Field(default_factory=list)

    creation: datetime
    modified: datetime