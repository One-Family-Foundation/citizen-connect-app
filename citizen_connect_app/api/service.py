import frappe

from citizen_connect_app.services.service import ServiceManager
from samaaja.api.common import custom_response


@frappe.whitelist(allow_guest=True)
def get(limit=10, offset=0):
    try:
        data = ServiceManager.get_list(
            limit=limit,
            offset=offset
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
def get_category(category, limit=10, offset=0):
    try:
        data = ServiceManager.get_category(
            category=category,
            limit=limit,
            offset=offset
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