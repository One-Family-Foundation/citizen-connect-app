import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.request_help import RequestHelpManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def create():
    try:
        data = frappe.form_dict
        attachment = frappe.request.files.get("file")

        return RequestHelpManager.create(
            request_data=data,
            request_type="service",
            attachment=attachment,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            status_code=500,
            error=True,
        )