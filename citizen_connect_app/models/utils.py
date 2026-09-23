import frappe

from pydantic import BaseModel, ValidationInfo, model_validator


class ItemResponse(BaseModel):
    name: str
    display_name: str | None = None

    @model_validator(mode="after")
    def set_display_name(self, info: ValidationInfo):
        lang = (info.context or {}).get("lang")
        self.display_name = frappe._(self.name, lang=lang)
        return self


class CategoryResponse(BaseModel):
    l1: ItemResponse | None = None
    l2: ItemResponse | None = None


class LocationResponse(BaseModel):
    country: ItemResponse | None = None
    geo1: ItemResponse | None = None
    geo2: ItemResponse | None = None


class MediaResponse(BaseModel):
    media: str
    caption: str | None = None

class Category(BaseModel):
    l1:str | None = None
    l2:str | None = None 

class Location(BaseModel):
    country:str | None = None
    geo1:str | None = None
    geo2:str | None = None
