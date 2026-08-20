from typing import Optional
from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator


class NGO(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class CategoryChild(BaseModel):
    category: str


class Category(BaseModel):
    id: str
    catalogue_name: str
    category_level: str


class NGOAdmin(BaseModel):
    user: str
    is_active: bool = True


class Organisation(BaseModel):
    id: str

    org_name: str
    short_name: Optional[str] = None

    category_l1: list[CategoryChild] = Field(
        default_factory=list
    )

    category_l2: list[CategoryChild] = Field(
        default_factory=list
    )

    established: Optional[date] = None

    language: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    description: Optional[str] = None
    registered_address: Optional[str] = None
    registration_number: Optional[str] = None
    website_url: Optional[str] = None
    logo: Optional[str] = None

    is_active: bool = True

    ngo_admin: list[NGOAdmin] = Field(
        default_factory=list
    )

    country: Optional[str] = None
    geo_l1: Optional[str] = None
    geo_l2: Optional[str] = None

    @field_validator("org_name", "short_name")
    @classmethod
    def clean_names(cls, value: Optional[str]):
        if value is None:
            return None
        return value.strip()

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: Optional[str]):
        if value is None:
            return None
        return value.strip()

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: Optional[str]):
        if value is None:
            return None
        return value.strip().lower()