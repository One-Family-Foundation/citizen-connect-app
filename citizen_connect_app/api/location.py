import frappe
from samaaja.utils.result import Result
from citizen_connect_app.services.location import LocationManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def get_locations():
    try:
        # If LocationManager already returns a Result object, 
        # just convert it directly to your custom response.
        return LocationManager.get_locations().to_custom_response()

    except Exception as e:
        ErrorLogger.log(
            message="Failed to fetch locations",
            details=str(e),
            stacktrace=frappe.get_traceback()
        )

        return Result.error(
            "Unable to fetch locations."
        ).to_custom_response()