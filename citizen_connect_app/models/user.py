from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Annotated
from citizen_connect_app.models.utils import Location


class User(BaseModel):
    full_name: Annotated[str, Field(min_length=3, max_length=120)]
    email: EmailStr
    mobile_no: Optional[Annotated[str, Field(min_length=6, max_length=15)]] = None
    location: Optional[Location] = None

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str):
        return value.strip()

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str):
        return value.strip().lower()

    @field_validator("mobile_no")
    @classmethod
    def clean_mobile(cls, value: Optional[str]):
        if value is None:
            return value
        return value.strip()