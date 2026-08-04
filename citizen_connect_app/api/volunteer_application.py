import frappe

from citizen_connect_app.services.opportunity_application import OpportunityApplicationManager
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.custom_response import custom_response


@frappe.whitelist(allow_guest=True)
def apply():
    try:
        data = frappe.form_dict
        attachment = frappe.request.files.get("file")

        return OpportunityApplicationManager.create(
            data=data,
            attachment=attachment,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            status_code=500,
            error=True,
        )