import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.service import ServiceManager
from citizen_connect_app.utils.error_logger import ErrorLogger

@frappe.whitelist(allow_guest=True)
def get(
    limit=10,
    offset=0,
    category_l1=None,
    category_l2=None,
    country=None,
    geo1=None,
    geo2=None,
):
    try:
        return ServiceManager.get_list(
            limit=limit,
            offset=offset,
            category_l1=category_l1,
            category_l2=category_l2,
            country=country,
            geo1=geo1,
            geo2=geo2,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(
            message="Failed to fetch services",
            stacktrace=frappe.get_traceback(),
        )

        return custom_response(
            message="Failed to fetch services",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )

@frappe.whitelist(allow_guest=True)
def detail(service_id):
    try:
        return ServiceManager.get(service_id).to_custom_response()

    except Exception as e:
        ErrorLogger.log(
            message="Failed to fetch service",
            stacktrace=frappe.get_traceback(),
        )

        return custom_response(
            message="Failed to fetch service",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )

@frappe.whitelist(allow_guest=True)
def get_categories():
    try:
        return ServiceManager.get_categories().to_custom_response()

    except Exception as e:
        ErrorLogger.log(
            message="Failed to fetch categories",
            stacktrace=frappe.get_traceback(),
        )

        return custom_response(
            message="Failed to fetch categories",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )
