import json

import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.issue_manager import create
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def create_issue():
    try:
        data = {
            "user_id": frappe.form_dict.get("user_id"),
            "description": frappe.form_dict.get("description"),
            "urgency": frappe.form_dict.get("urgency"),
            "allow_contact": frappe.form_dict.get("allow_contact"),
            "location": json.loads(frappe.form_dict.get("location")),
            "category": json.loads(frappe.form_dict.get("category")),
            "files": [f for f in frappe.request.files.getlist("files") if f.filename]
        }

        return create(issue_data=data).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while creating the report issue.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )