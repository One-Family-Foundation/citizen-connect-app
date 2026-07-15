import frappe
from citizen_connect.services.service import ServiceManager
from citizen_connect.utils.result import Result


@frappe.whitelist(allow_guest=True)
def get(limit=10, offset=0):
    try:
        return ServiceManager.get(limit=limit, offset=offset).to_custom_response()
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed to fetch services"
        )
        return Result.failure(
            message="Failed to fetch services",
            error_data=str(e)
        ).to_custom_response()