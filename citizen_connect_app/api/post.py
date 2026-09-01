import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.post_manager import( create_post , get_list , get_user_post)
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
@frappe.whitelist(allow_guest=True)
def feed(
    limit=10,
    offset=0,
    category_l1=None,
    country=None,
    geography_l1=None,
    geography_l2=None,
    lang="en"
):
    try:
        return get_list(
            limit=limit,
            offset=offset,
            category_l1=category_l1,
            country=country,
            geography_l1=geography_l1,
            geography_l2=geography_l2,
            lang=lang
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            status_code=500,
            message="An error occurred while fetching posts.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )
@frappe.whitelist(allow_guest=True)
def user_posts(
    user_id,
    limit=10,
    offset=0,
):
    try:
        return get_user_post(
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