import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.post_manager import create_post
from citizen_connect_app.utils.error_logger import ErrorLogger
import json

@frappe.whitelist()
def create():
    try:
        data = {
            "description": frappe.form_dict.get("description"),
            "location": json.loads(frappe.form_dict.get("location")),
            "category": json.loads(frappe.form_dict.get("category")),
            "files": [f for f in frappe.request.files.getlist("files") if f.filename]
        }
    
        return create_post(post_data=data).to_custom_response()
    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while creating the post.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()}
        )