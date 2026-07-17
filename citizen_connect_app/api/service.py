import frappe

from citizen_connect_app.services.service import ServiceManager
from samaaja.api.common import custom_response


@frappe.whitelist(allow_guest=True)
def get(
    limit=10,
    offset=0,
    category_l1=None,
    category_l2=None,
    country=None,
    geo1=None,
    geo2=None
):
    try:
        data = ServiceManager.get_list(
            limit=limit,
            offset=offset,
            category_l1=category_l1,
            category_l2=category_l2,
            country=country,
            geo1=geo1,
            geo2=geo2
        )

        return custom_response(
            message="Services fetched successfully",
            data=data
        )

    except Exception as e:
        return custom_response(
            message="Failed to fetch services",
            error=str(e)
        )


@frappe.whitelist(allow_guest=True)
def get_categories():
    try:
        data = ServiceManager.get_categories()

        return custom_response(
            message="Categories fetched successfully",
            data=data
        )

    except Exception as e:
        return custom_response(
            message="Failed to fetch categories",
            error=str(e)
        )