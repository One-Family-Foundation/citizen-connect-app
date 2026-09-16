import frappe

from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.models.profile_model import (UserProfile , UserProfileResponse)
from citizen_connect_app.utils.commons import resolve_location
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.services.post_manager import count_user_post
from citizen_connect_app.services.opportunity_application import count_volunteer_actions
from citizen_connect_app.services.case_manager import (get_user_case_count , get_case_resolved_count )
from citizen_connect_app.utils.commons import create_media_url
from citizen_connect_app.services.gamification_manager import (get_cached_user_rank)

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
        uploaded_file = frappe.request.files.get("profile_photo")

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
        if uploaded_file:
            file_doc = frappe.get_doc({
               "doctype": "File",
               "file_name": uploaded_file.filename,
               "attached_to_doctype": "User",
               "attached_to_name": user.name,
               "content": uploaded_file.read(),
               "is_private": 0,
            })

            file_doc.insert(ignore_permissions=True)

            profile.profile_photo = file_doc.file_url
            user.user_image = file_doc.file_url

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
            if field == "phone":
                 profile.phone = value   
            else:     
                setattr(profile, field, value)

        profile.save(ignore_permissions=True)
        user.save(ignore_permissions=True)
        

        return Result.success(
            message="Profile updated successfully.",
            data={
                "id": profile.name,
                "user": user.name,
                "full_name": user.full_name,
                "email": user.email,
                "phone": profile.phone or user.mobile_no,
                "profile_photo": user.user_image,
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


def get_profile(user_id: str, lang: str = "en") -> Result:
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
        rank = get_cached_user_rank(user.name) or 0

        profile_image = create_media_url(user.user_image) if user.user_image else None

        user_badges = frappe.get_all(
            "User Badge",
            filters={
                "user": user.name,
            },
            fields=["badge","badge_count"],
            distinct=True,
        )

        badges = []

        for user_badge in user_badges:
            badge = frappe.db.get_value(
                "Badge",
                user_badge.badge,
                ["name", "title", "icon", "description"],
                as_dict=True,
            )

            if badge:
                badge_icon = create_media_url(badge.icon)
                badges.append({
                    "id": badge.name,
                    "title":{
                        "name": badge.title,
                    },
                    "icon": badge_icon,
                })

        geo1_name = None
        geo2_name = None

        if profile.geo_l1:
            geo1_name = frappe.db.get_value(
                "Geography L1",
                profile.geo_l1,
                "geo_l1",
            )

        if profile.geo_l2:
            geo2_name = frappe.db.get_value(
                "Geography L2",
                profile.geo_l2,
                "geo_l2",
            )

        
        case_actions = get_user_case_count(user.name) or 0
        resolved_counts = get_case_resolved_count(user.name) or 0

        volunteer_result = count_volunteer_actions(
            user.name
        )

        opportunity_actions = volunteer_result.data or 0
        post_result = count_user_post(
            user.name
        )

        post_count = post_result.data or 0

        actions = (
            case_actions
            + opportunity_actions
        )

        top_categories = frappe.get_all(
            "User Category Statistics",
            filters={
                "user": user.name
            },
            fields=[
                "category_l1",
                "count"
            ],
            order_by="count desc",
            limit_page_length=3,
        )

        categories = []

        for item in top_categories:
            category_name = frappe.db.get_value(
                "Category",
                item.category_l1,
                "name"
            )

            if category_name:
                categories.append(
                    {
                        "l1":{
                            "name": category_name
                        }
                    }
                )

        profile_data = {
            "user_info": {
                "id": profile.name,
                "user": user.name,
                "full_name": user.full_name,
                "alternative_email": profile.alternative_email,
                "phone": profile.phone,
                "type": profile.user_type,
                "profile_image": profile_image,
                "org_name": profile.org_name,

                "location": {
                    "country": {
                        "name": profile.country
                    },
                    "geo1": {
                        "name": geo1_name
                    }if geo1_name else None,
                    "geo2": {
                        "name": geo2_name
                    }if geo2_name else None,
                },

                "interests": categories,
            },

            "stats": {
                "actions": actions,
                "resolved": resolved_counts,
                "posts": post_count,
                "rank": rank,
            },

            "badges": badges,

            "leaderboard": {
                "rank": rank
            },

            "activity_counts": {
                "cases": case_actions,
                "actions": opportunity_actions,
                "posts": post_count,
            },
        }
        profile_response = UserProfileResponse.model_validate(
            profile_data,
            context={"lang": lang}
        )

        return Result.success(
            message="Profile fetched successfully.",
            data=profile_response.model_dump(),
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch profile.",
            data={
                "error": str(e)
            },
            error_data={
                "traceback": frappe.get_traceback()
            },
        )