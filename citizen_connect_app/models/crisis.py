from typing import Optional
from datetime import date

from pydantic import BaseModel, Field

from citizen_connect_app.models.utils import Location


class CrisisMedia(BaseModel):
    media: Optional[str] = None
    caption: Optional[str] = None


class CrisisImpact(BaseModel):
    impact_title: Optional[str] = None
    impact_number: Optional[int] = None
    impact_type: Optional[str] = None


class ResourceRequirement(BaseModel):
    resource_name: str
    quantity_requirement: Optional[int] = None
    qunatity_recieved: Optional[int] = None
    unit: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None


class EmergencyContact(BaseModel):
    agency_name: str
    contact_number: str
    agency_category: Optional[str] = None


class UserChildTable(BaseModel):
    user: Optional[str] = None
    is_active: Optional[bool] = None


class DonationDetails(BaseModel):
    fund_name: Optional[str] = None
    description: Optional[str] = None
    external_donation_link: Optional[str] = None
    ngo: Optional[str] = None
    is_verified: Optional[bool] = None
    total_donation_target: Optional[int] = None
    currency:Optional[str]=None


class CrisisVolunteerOpportunity(BaseModel):
    child_vol_opportunity: Optional[str] = None
    num_of_volunteer: Optional[int] = None
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    volunteer_format: Optional[str] = None


class ResourceDropoffLocation(BaseModel):
    person_name: Optional[str] = None
    phone_num: Optional[str] = None
    time: Optional[str] = None
    location_name: Optional[str] = None
    location_address:Optional[str]=None


class Crisis(BaseModel):
    id: str
    title: str
    category:str
    media: list[CrisisMedia] = Field(default_factory=list)

    description: Optional[str] = None

    location: Location

    start_date: Optional[date] = None

    impact: list[CrisisImpact] = Field(default_factory=list)

    resources_needed: list[ResourceRequirement] = Field(
        default_factory=list
    )

    emergency_contacts: list[EmergencyContact] = Field(
        default_factory=list
    )

    status: str

    collaborators: list[UserChildTable] = Field(
        default_factory=list
    )

    crisis_summary: Optional[str] = None

    donation_opportunity: list[DonationDetails] = Field(
        default_factory=list
    )

    volunteer_opportunity: list[CrisisVolunteerOpportunity] = Field(
        default_factory=list
    )

    verification_status: Optional[str] = None

    resource_dropoff_location: Optional[ResourceDropoffLocation] = None


class CrisisSummary(BaseModel):
    id: str
    title: str
    category:str
    media: list[CrisisMedia] = Field(default_factory=list)
    crisis_summary: Optional[str] = None
    impact: list[CrisisImpact] = Field(default_factory=list)
    location: Location

    start_date: Optional[date] = None

    status: str

    verification_status: Optional[str] = None