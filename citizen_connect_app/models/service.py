from citizen_connect_app.models.utils import Location, Category
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServiceResponse(BaseModel):
    id: str
    title: str
    description: str
    location: Location
    cost_model: str
    cost_details: float
    sponsorship_information: str | None = None
    availability_status: str
    service_channel: str
    service_status: str
    creation: datetime
    eligibility_condition: str | None = None
    rating: float
    ngo_name: str
    service_category: Category

    def to_dict(self):
        return asdict(self)