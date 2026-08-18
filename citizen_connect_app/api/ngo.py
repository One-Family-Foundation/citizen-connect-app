import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.NGO_profile_manager import get_profile
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def get(organisation_id=None):
    try:
        if not organisation_id:
            return custom_response(
                message="Organisation ID is required.",
                status_code=400,
                error=True,
            )

        result = get_profile(
            organisation=organisation_id
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch organisation profile.",
            status_code=500,
            error=True,
        )