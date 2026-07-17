import frappe
from samaaja.utils.result import Result
from citizen_connect_app.services.location import LocationManager


@frappe.whitelist(allow_guest=True)
def get_locations():
    try:
        locations = LocationManager.get_locations()

        return Result.success({
            "locations": locations
        })

    except Exception:
        return Result.failure(
            message="Unable to fetch locations."
        )