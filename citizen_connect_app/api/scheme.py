import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.scheme import SchemeManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def get_list1(
    limit=10,
    offset=0,
    country=None,
    category_l1=None,
    category_l2=None,
    geo1=None,
    geo2=None,
    gender=None,
    disabled=None,
    verified=None,
    active=None,
):
    try:
        return SchemeManager.get_list(
            category_l1=category_l1,
            category_l2=category_l2,
            limit=limit,
            offset=offset,
            country=country,
            geo1=geo1,
            geo2=geo2,
            gender=gender,
            disabled=disabled,
            verified=verified,
            active=active,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch schemes",
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def get1(scheme_id):
    try:
        return SchemeManager.get(scheme_id).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch scheme",
            status_code=500,
            error=True,
        )