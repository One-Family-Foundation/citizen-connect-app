import frappe
from typing import Optional
from pydantic import BaseModel
from datetime import datetime 

class Location(BaseModel):
    country: Optional[str] = None
    geo1: Optional[str] = None
    geo2: Optional[str] = None

class Category(BaseModel):
    l1: Optional[str] = None
    l2: Optional[str] = None