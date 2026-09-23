import frappe
import json

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.volunteer_action_manager import (create_volunteer_action , get_user_actions)
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist()
def create():
    try:
        category = frappe.form_dict.get("category")
        description = frappe.form_dict.get("description")

        frappe.logger("citizen_connect_app").info(
            f"category = {category}"
        )
        frappe.logger("citizen_connect_app").info(
            f"description = {description}"
        )

        data = {
            "description": description,
            "category": json.loads(category) if category else None,
            "location": (
                json.loads(frappe.form_dict.get("location"))
                if frappe.form_dict.get("location")
                else None
            ),
            "start_date": frappe.form_dict.get("start_date") or None,
            "end_date": frappe.form_dict.get("end_date") or None,
            "media": [
                f
                for f in frappe.request.files.getlist("files")
                if f.filename
            ],
        }

        frappe.logger("citizen_connect_app").info(
            f"Volunteer action data = {data}"
        )

        return create_volunteer_action(
            volunteer_action_data=data
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            status_code=500,
            message="An error occurred while creating the volunteer action.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )

@frappe.whitelist(allow_guest=True)
def user_actions(
    user_id,
    limit=10,
    offset=0,
):
    try:
        return get_user_actions(
            user_id=user_id,
            limit=limit,
            offset=offset,
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while fetching user posts.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )