
import frappe
from samaaja.utils.result import Result
from citizen_connect_app.models.utils import Location

def resolve_location(location:Location)->Result:
    country = None
    geo_l1 = None
    geo_l2 = None
    
    if location.country:
        country = frappe.db.get_value(
            "Country",
            {"country_name": location.country},
            "name"
        )
        if not country:
            return Result.bad_request(
                message="Invalid country selected."
        )
        if location.geo1:
            geo_l1 = frappe.db.get_value(
                "Geography L1",
                {"geo_l1": location.geo1},
                "name"
            )
            if not geo_l1:
                return Result.bad_request(
                message="Invalid Geography L1 selected."
            )
            if location.geo2:
                geo_l2 = frappe.db.get_value(
                    "Geography L2",
                    {"geo_2": location.geo2},
                    "name"
                )
            if not geo_l2:
                return Result.bad_request(
                    message="Invalid Geography L2 selected."
                )
    return Result.success(message="Location resolved successfully.", data=Location(country=country, geo1=geo_l1, geo2=geo_l2),)