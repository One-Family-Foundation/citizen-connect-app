import frappe

from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger


def create_rating(category: str, item_id: str, rating) -> Result:
    try:
        # Get logged-in user
        user = frappe.session.user

        if not user or user == "Guest":
            return Result.failure("Login required to rate.")

        # Validate category
        allowed_categories = ["Scheme", "Service"]

        if category not in allowed_categories:
            return Result.failure(
                "Invalid category. Allowed values are Scheme or Service."
            )

        # Validate item ID
        if not item_id:
            return Result.failure("Item ID is required.")

        # Get Scheme/Service document using ORM
        if not frappe.db.exists(category, item_id):
            return Result.failure(f"{category} not found.")

        item_doc = frappe.get_doc(category, item_id)

        # Validate rating
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return Result.failure("Rating must be a valid number.")

        if rating < 1 or rating > 5:
            return Result.failure("Rating must be between 1 and 5.")

        # Check whether user already rated this item
        existing_rating = frappe.db.exists(
            "Rating",
            {
                "user_id": user,
                "category": category,
                "id": item_id,
            },
        )

        if existing_rating:
            return Result.failure(
                f"You have already rated this {category.lower()}."
            )

        # Get current values from ORM document
        total_users = item_doc.total_users or 0
        total_rating_sum = item_doc.total_rating_sum or 0

        # Calculate new values
        total_users += 1
        total_rating_sum += rating

        new_rating = total_rating_sum / total_users

        # Update document using ORM
        item_doc.total_users = total_users
        item_doc.total_rating_sum = total_rating_sum
        item_doc.rating = new_rating

        item_doc.save(ignore_permissions=True)

        # Create Rating document using ORM
        rating_doc = frappe.get_doc(
            {
                "doctype": "Rating",
                "user_id": user,
                "category": category,
                "id": item_id,
                "rating": rating,
            }
        )

        rating_doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return Result.success(
            "Rating submitted successfully.",
            {
                "id": rating_doc.name,
                "user_id": user,
                "category": category,
                "item_id": item_id,
                "rating": rating,
            },
        )

    except Exception as e:
        frappe.db.rollback()
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to submit rating.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )