import frappe

from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.models.profile_model import UserProfile
from citizen_connect_app.utils.commons import resolve_location
from citizen_connect_app.utils.error_logger import ErrorLogger


def update_profile(profile_data: dict) -> Result:
    try:
        if not frappe.session.user or frappe.session.user == "Guest":
            return Result.bad_request(
                message="User must be logged in."
            )

        user_email = frappe.session.user

        if not frappe.db.exists("User", user_email):
            return Result.bad_request(
                message="User not found."
            )

        user = frappe.get_doc("User", user_email)

        profile_name = frappe.db.get_value(
            "User Profile",
            {"user": user.name},
            "name",
        )

        if not profile_name:
            return Result.bad_request(
                message="User profile not found."
            )

        try:
            profile_data = UserProfile(**profile_data)

        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]

            return Result.bad_request(
                message="; ".join(messages)
            )

        profile = frappe.get_doc(
            "User Profile",
            profile_name
        )

        update_data = profile_data.model_dump(
            exclude_unset=True
        )

        if "location" in update_data:
            location = profile_data.location

            update_data.pop("location")

            if location is None:
                profile.country = None
                profile.geo_l1 = None
                profile.geo_l2 = None

            else:
                location_result = resolve_location(location)

                if location_result.is_bad_request:
                    return location_result

                profile.country = location_result.data.country
                profile.geo_l1 = location_result.data.geo1
                profile.geo_l2 = location_result.data.geo2

        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.save(ignore_permissions=True)

        return Result.success(
            message="Profile updated successfully.",
            data={
                "id": profile.name,
                "user": user.name,
                "full_name": user.full_name,
                "email": user.email,
                "phone": profile.phone or user.mobile_no,
                "profile_photo": profile.profile_photo,
                "alternative_email": profile.alternative_email,
                "user_type": profile.user_type,
                "location": {
                    "country": profile.country,
                    "geo1": profile.geo_l1,
                    "geo2": profile.geo_l2,
                },
                "org_name": profile.org_name,
            },
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to update profile.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback()
            },
        )

          