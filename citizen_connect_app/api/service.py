import frappe

from citizen_connect_app.services.service import ServiceManager
from samaaja.api.common import custom_response


@frappe.whitelist(allow_guest=True)
def get(limit=10, offset=0):
    result = ServiceManager.get_list(
        limit=limit,
        offset=offset
    )

    return result.to_custom_response()
