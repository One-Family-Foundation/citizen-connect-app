import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.post_manager import create_post
from citizen_connect_app.utils.error_logger import ErrorLogger

@frappe.whitelist()
def create_post():
    data = {
        "description": frappe.form_dict.get("description"),
        "location": frappe.form_dict.get("location"),
        "category": frappe.form_dict.get("category"),
        "files": frappe.request.files.getlist("files")
    }
    return create_post(post_data=data).to_custom_response()