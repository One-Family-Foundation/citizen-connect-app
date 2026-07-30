from typing import Optional
from pydantic import BaseModel

class NGO(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None