import frappe

from pydantic import BaseModel, ValidationInfo, model_validator


class Item(BaseModel):
    name: str
    display_name: str | None = None

    @model_validator(mode="after")
    def set_display_name(self, info: ValidationInfo):
        lang = (info.context or {}).get("lang")
        self.display_name = frappe._(self.name, lang=lang)
        return self


class Category(BaseModel):
    l1: Item | None = None
    l2: Item | None = None


class Location(BaseModel):
    country: Item | None = None
    geo1: Item | None = None
    geo2: Item | None = None

class MediaResponse(BaseModel):
    media: str
    caption: str | None = None