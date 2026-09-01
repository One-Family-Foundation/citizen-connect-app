
import frappe

from citizen_connect_app.services.case_manager import get_user_case_list
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.custom_response import custom_response

@frappe.whitelist(allow_guest=True)
def get(
    user_id,
    status="All",
     limit=10,
    offset=0,
):
    try:
        return get_user_case_list(
            user_id=user_id,
            status=status,
            limit=limit,
           offset=offset,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while fetching user requests.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )