        
from typing import Optional, Annotated
from citizen_connect_app.models.utils import ItemResponse,CategoryResponse, LocationResponse , Location
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
)

class UserProfile(BaseModel):

    profile_photo: Optional[str] = None

    alternative_email: Optional[EmailStr] = None

    phone: Optional[
        Annotated[
            str,
            Field(min_length=6, max_length=15)
        ]
    ] = None

    user_type: Optional[str] = None

    location: Optional[Location] = None

    org_name: Optional[str] = None

    @field_validator("alternative_email", mode="before")
    @classmethod
    def clean_alternative_email(cls, value):
        if value == "":
            return None

        if value is None:
            return None

        return value.strip().lower()

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, value):
        if value == "":
            return None

        if value is None:
            return None

        return value.strip()

    @field_validator("user_type", mode="before")
    @classmethod
    def validate_user_type(cls, value):
        if value is None or value == "":
            return None

        value = value.strip()

        if value not in ["Citizen", "Volunteer"]:
            raise ValueError(
                "User type must be Citizen or Volunteer."
            )

        return value

    @field_validator("org_name", mode="before")
    @classmethod
    def clean_org_name(cls, value):
        if value == "":
            return None

        if value is None:
            return None

        return value.strip()

    @field_validator("location", mode="before")
    @classmethod
    def empty_location_to_none(cls, value):
        if value == "":
            return None

        return value


class ProfileBadge(BaseModel):
    id: str
    title: ItemResponse | None = None
    icon: Optional[str] = None


class ProfileUserInfo(BaseModel):
    id: str
    user: str
    full_name: Optional[str] = None
    alternative_email: Optional[EmailStr] = None
    type: Optional[str] = "Citizen"
    profile_image: Optional[str] = None
    org_name: Optional[str] = None
    location: LocationResponse | None = None
    interests: list[CategoryResponse] = Field(default_factory=list)

class ProfileStats(BaseModel):
    actions: int = 0
    resolved: int = 0
    posts: int = 0
    rank: int = 0


class ProfileLeaderboard(BaseModel):
    rank: int = 0


class ProfileActivityCounts(BaseModel):
    cases: int = 0
    actions: int = 0
    posts: int = 0


class UserProfileResponse(BaseModel):
    user_info: ProfileUserInfo
    stats: ProfileStats
    badges: list[ProfileBadge] = Field(default_factory=list)
    leaderboard: ProfileLeaderboard
    activity_counts: ProfileActivityCounts