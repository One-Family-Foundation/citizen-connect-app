
from typing import Optional, Annotated
from datetime import date

from pydantic import BaseModel, Field, EmailStr, field_validator

from citizen_connect_app.models.utils import Category, Location
from citizen_connect_app.models.ngo import NGO

class Skill(BaseModel):
    skill_name: str
    
class Opportunity(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    skills: list[Skill] = []

    category: Category

    crisis_link: Optional[str] = None
    language:Optional[str]=None
    location: Location

    volunteer_format: Optional[str] = None
    expected_time: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    compensation_type: Optional[str] = None

    ngo: Optional[NGO] = None

    rating: Optional[float] = None

    status: str


class OpportunitySummary(BaseModel):
    id: str

    title: str
    description: Optional[str] = None

    category: Category
    language: Optional[str] = None
    location: Location

    volunteer_format: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    compensation_type: Optional[str] = None

    rating: Optional[float] = None

    status: str


class GuestOpportunityForm(BaseModel):
    opportunity_id: str

    full_name: Annotated[str, Field(min_length=3, max_length=120)]
    email: EmailStr
    phone: Optional[Annotated[str, Field(min_length=6, max_length=15)]] = None

    age: int
    gender: str
    description: Annotated[str, Field(max_length=500)]

    attachment: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str):
        return value.strip()

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str):
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: str):
        return value.strip()


class LoggedInOpportunityForm(BaseModel):
    opportunity_id: str

    phone: Optional[Annotated[str, Field(min_length=6, max_length=15)]] = None

    age: int
    gender: str
    description: Annotated[str, Field(max_length=500)]

    attachment: Optional[str] = None

    @field_validator("phone", mode="before")
    @classmethod
    def empty_phone_to_none(cls, value):
        if value == "":
            return None
        return value

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: Optional[str]):
        if value is None:
            return None
        return value.strip()