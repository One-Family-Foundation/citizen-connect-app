import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.rating_manager import create_rating
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist()
def create():
        try:
            category = frappe.form_dict.get("category")
            item_id = frappe.form_dict.get("item_id")
            rating = frappe.form_dict.get("rating")

            return create_rating(
                category=category,
                item_id=item_id,
                rating=rating,
            ).to_custom_response()

        except Exception as e:
            ErrorLogger.log(e)

            return custom_response(
                status_code=500,
                message="An error occurred while submitting the rating.",
                data={"error": str(e)},
                error_data={"traceback": frappe.get_traceback()},
            )