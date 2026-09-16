from typing import Optional

from pydantic import BaseModel, Field, model_validator, EmailStr


class RequestHelp(BaseModel):

    service_name: Optional[str] = None

    scheme_name: Optional[str] = None

    full_name: str = Field(..., min_length=3, max_length=120)

    email_id: EmailStr

    mobile_num:Optional[str] = Field(None, min_length=6, max_length=15)

    gender: Optional[str] = None

    age: Optional[str] = None

    description: Optional[str] = None

    country: Optional[str] = None

    geo_l1: Optional[str] = None

    geo_l2: Optional[str] = None

    @model_validator(mode="after")
    def validate_request_type(self):
        if not self.service_name and not self.scheme_name:
            raise ValueError(
                "Either service_name or scheme_name is required"
            )

        if self.service_name and self.scheme_name:
            raise ValueError(
                "Only one of service_name or scheme_name can be provided"
            )

        return self