import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.volunteer_opportunity import OpportunityManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def get_list(
    limit=10,
    offset=0,
    category_l1=None,
    category_l2=None,
    country=None,
    geo1=None,
    geo2=None,
    volunteer_format=None,
    compensation_type=None,
    status=None,
):
    try:
        return OpportunityManager.get_list(
            limit=limit,
            offset=offset,
            category_l1=category_l1,
            category_l2=category_l2,
            country=country,
            geo1=geo1,
            geo2=geo2,
            volunteer_format=volunteer_format,
            compensation_type=compensation_type,
            status=status,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch volunteer opportunities",
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def get(opportunity_id):
    try:
        return OpportunityManager.get(opportunity_id).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch volunteer opportunity",
            status_code=500,
            error=True,
        )