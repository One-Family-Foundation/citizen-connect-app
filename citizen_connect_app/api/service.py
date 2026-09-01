import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.service import ServiceManager
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
    lang="en",
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
            lang=lang,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch services",
            status_code=500,
            error=True,
        )

@frappe.whitelist(allow_guest=True)
def get(service_id, lang="en"):
    try:
        return ServiceManager.get(service_id, lang=lang).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch service",
            status_code=500,
            error=True,
        )

@frappe.whitelist(allow_guest=True)
def get_categories(lang="en"):
    try:
        return ServiceManager.get_categories(lang=lang).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch categories",
            status_code=500,
            error=True,
        )
