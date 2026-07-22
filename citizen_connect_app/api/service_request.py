import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.service_request import ServiceRequestManager
from citizen_connect_app.utils.error_logger import ErrorLogger

@frappe.whitelist(allow_guest=True)
def create_service_request():
    try:
        data = frappe.request.get_json()

        return ServiceRequestManager.create(data).to_custom_response()

    except Exception as e:
        ErrorLogger.log(
            message="Create Service Request API Error",
            details=str(e),
            stacktrace=frappe.get_traceback(),
        )
        return custom_response(
            message="Something went wrong.",
            is_internal_server_error=True,
            data={"error": str(e)},
        )


