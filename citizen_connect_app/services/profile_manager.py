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
        print("========== UPDATE PROFILE ==========")
        print("UPDATE DATA:", update_data)
        print("PHONE BEFORE:", profile.phone)

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
            if field == "phone":
                 profile.phone = value
            else:     
                setattr(profile, field, value)

        print("PHONE AFTER SET:", profile.phone)
        profile.save(ignore_permissions=True)
        print("PHONE AFTER SAVE:", profile.phone)

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
def get_profile(user_id: str) -> Result:
    """
    Fetch public profile.
    Guest users can access this profile.
    """

    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        if not frappe.db.exists("User", user_id):
            return Result.bad_request(
                message="User not found."
            )

        user = frappe.get_doc(
            "User",
            user_id
        )

        profile_name = frappe.db.get_value(
            "User Profile",
            {"user": user.name},
            "name",
        )

        if not profile_name:
            return Result.bad_request(
                message="User profile not found."
            )

        profile = frappe.get_doc(
            "User Profile",
            profile_name
        )

        profile_data = {
            "user_info": {
                "id": profile.name,
                "user": user.name,
                "name": user.full_name,
                "phone":profile.phone,
                "role": profile.user_type or "Citizen",
                "profile_image": profile.profile_photo,
                "org_name": profile.org_name,

                "location": {
                    "country": profile.country,
                    "geo1": profile.geo_l1,
                    "geo2": profile.geo_l2,
                },

                # Dummy data
                "interests": [
                    "Cleanliness Drives",
                    "Fundraising",
                    "Youth Counseling",
                ],
            },

            # Dummy statistics
            "stats": {
                "actions": 24,
                "resolved": 10,
                "posts": 8,
                "rank": "#8",
            },

            # Dummy badges
            "badges": [
                {
                    "id": "community_starter",
                    "title": "Community Starter",
                    "icon": "add-circle-outline",
                },
                {
                    "id": "first_action",
                    "title": "First Action",
                    "icon": "leaf-outline",
                },
                {
                    "id": "water_champion",
                    "title": "Water Champion",
                    "icon": "water-outline",
                },
                {
                    "id": "active_volunteer",
                    "title": "Active Volunteer",
                    "icon": "heart-handshake-outline",
                },
            ],

            "leaderboard": {
                "rank": 8,
                "message": "You're #8 this month",
            },

            "activity_counts": {
                "cases": 3,
                "actions": 2,
                "posts": 2,
            },

            # Dummy cases
            "cases": [
                {
                    "id": "CASE-001",
                    "title": "Broken Street Light @ MG Road",
                    "status": "In Progress",
                    "type": "case",
                },
                {
                    "id": "CASE-002",
                    "title": "Water Leakage Near Ward 4 Park",
                    "status": "Resolved",
                    "type": "case",
                },
                {
                    "id": "CASE-003",
                    "title": "Request for Anganwadi Teacher",
                    "status": "Pending Review",
                    "type": "case",
                },
            ],

            # Dummy actions
            "actions": [
                {
                    "id": "ACT-001",
                    "title": "Tree Plantation Drive",
                    "category": "Biodiversity & Ecosystems",
                    "likes": 128,
                    "comments": 14,
                    "date": "Apr 2",
                    "status": "Completed",
                },
                {
                    "id": "ACT-002",
                    "title": "Water Quality Survey",
                    "category": "Water Quality & Conservation",
                    "likes": 128,
                    "comments": 14,
                    "date": "Apr 2",
                    "status": "Completed",
                },
            ],

            # Dummy posts
            "posts": [
                {
                    "id": "POST-001",
                    "title": "Cleanliness drive at Ward 4 was a success!",
                    "likes": 128,
                    "comments": 14,
                    "date": "Apr 2",
                    "status": "Published",
                },
            ],
        }

        return Result.success(
            message="Profile fetched successfully.",
            data=profile_data,
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch profile.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback()
            },
        )