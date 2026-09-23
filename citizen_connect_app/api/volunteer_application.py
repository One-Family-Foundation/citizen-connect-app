import frappe

from citizen_connect_app.services.opportunity_application import OpportunityApplicationManager
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.opportunity_application import get_volunteer_actions

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
@frappe.whitelist(allow_guest=True)
def get_user_actions():
    try:
        user_id = frappe.form_dict.get("user_id")

        return get_volunteer_actions(
            user_id=user_id
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            status_code=500,
            error=True,
        )