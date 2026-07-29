import frappe
from typing import Optional
from pydantic import BaseModel, HttpUrl , Field
from datetime import datetime 
from citizen_connect_app.models.utils import Category, Location
from citizen_connect_app.models.ngo import NGO

class Scheme(BaseModel):
    id: str
    scheme_name: str
    description: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    documents_required: Optional[str] = None
    application_url: Optional[HttpUrl] = None

    location: Location

    gender: Optional[str] = None
    disabled_relevant: Optional[bool] = None
    income_limit: Optional[float] = None
    currency: Optional[str] = None
    issuing_body: Optional[str] = None

    is_active: bool
    is_verified: bool
    rating: Optional[float] = None

    creation: datetime
    modified: datetime

    scheme_category: Category

    ngos: list[NGO] = Field(default_factory=list)

class SchemeSummary(BaseModel):
    id: str
    scheme_name: str
    description: Optional[str] = None
    

    location: Location

    gender: Optional[str] = None
    disabled_relevant: Optional[bool] = None
    income_limit: Optional[float] = None
    currency: Optional[str] = None
    issuing_body: Optional[str] = None

    is_active: bool
    is_verified: bool
    rating: Optional[float] = None

    creation: datetime
    modified: datetime

    scheme_category: Category
