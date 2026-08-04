from typing import Optional
from datetime import date
from pydantic import BaseModel

from citizen_connect_app.models.utils import Category, Location
from citizen_connect_app.models.ngo import NGO


class Opportunity(BaseModel):
    id: str

    title: str
    description: Optional[str] = None
    skills: Optional[str] = None

    category: Category

    crisis_link: Optional[str] = None

    country: Optional[str] = None
    location: Location

    volunteer_format: Optional[str] = None  # On-site | Remote | Hybrid
    expected_time: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    compensation_type: Optional[str] = None  # Pro Bono | Stipend

    ngo: Optional[NGO] = None

    rating: Optional[float] = None

    status: str

class OpportunitySummary(BaseModel):
    id: str

    title: str
    description: Optional[str] = None

    category: Category

   
    location: Location

    volunteer_format: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    compensation_type: Optional[str] = None

    rating: Optional[float] = None

    status: str