import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.crisis_manager import (
    get_crisis_list,
    get_crisis,
)
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def get_list(
    limit=10,
    offset=0,
    country=None,
    geography_l1=None,
    geography_l2=None,
    status="Active",
):
    try:
        result = get_crisis_list(
            limit=limit,
            offset=offset,
            country=country,
            geography_l1=geography_l1,
            geography_l2=geography_l2,
            status=status,
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch crisis list.",
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def get(crisis_id=None):
    try:
        if not crisis_id:
            return custom_response(
                message="Crisis ID is required.",
                status_code=400,
                error=True,
            )

        result = get_crisis(
            crisis_id=crisis_id
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch crisis.",
            status_code=500,
            error=True,
        )