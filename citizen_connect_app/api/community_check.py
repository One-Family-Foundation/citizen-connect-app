import json

import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.community_check_manager import create
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def create_community_check():
    try:
        data = {
            "user_id": frappe.form_dict.get("user_id"),
            "title":frappe.form_dict.get("title"),
            "description":frappe.form_dict.get("description"),
            "water_supply": frappe.form_dict.get("water_supply"),
            "electricity": frappe.form_dict.get("electricity"),
            "road": frappe.form_dict.get("road"),
            "teacher_at_school": frappe.form_dict.get("teacher_at_school"),
            "healthcare": frappe.form_dict.get("healthcare"),
            "internet": frappe.form_dict.get("internet"),
            "sanitation": frappe.form_dict.get("sanitation"),
            "local_governance": frappe.form_dict.get("local_governance"),
            "confidence_level": frappe.form_dict.get("confidence_level"),
            "location": json.loads(frappe.form_dict.get("location")),
            "files": [f for f in frappe.request.files.getlist("files") if f.filename]
        }
        frappe.logger("citizen_connect_app").info(
            f"RAW LOCATION: {frappe.form_dict.get('location')}"
        )

        frappe.logger("citizen_connect_app").info(
            f"PARSED LOCATION: {data['location']}"
        )
        frappe.logger("citizen_connect_app").info(
            f"RAW DESCRIPTION: {frappe.form_dict.get('description')}"
        )

        return create(
            community_check_data=data
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while creating the community check.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )