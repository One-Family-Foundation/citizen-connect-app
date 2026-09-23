from pydantic import BaseModel
from typing import Optional


class IndividualLeaderboardItem(BaseModel):
    rank: int
    user_id: str
    user_name: str
    designation: Optional[str] = None
    profile_image: Optional[str] = None
    actions: int
    points: int

class GeographyLeaderboardItem(BaseModel):
    rank: int
    geography_id: str
    geography_name: str
    region: Optional[str] = None
    actions: int
    points: int


class IndividualLeaderboardResponse(BaseModel):
    users: list[IndividualLeaderboardItem]

class GeographyLeaderboardResponse(BaseModel):
    locations: list[GeographyLeaderboardItem]
