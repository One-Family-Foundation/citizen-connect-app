import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.location import LocationManager
from citizen_connect_app.utils.error_logger import ErrorLogger

@frappe.whitelist(allow_guest=True)
def get_locations():
    try:
        return LocationManager.get_list().to_custom_response()
    except Exception as e:
        ErrorLogger.log(
            message="Failed to fetch locations",
            stacktrace=frappe.get_traceback()
        )
        return custom_response(
            message="Failed to fetch locations",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )