import frappe
from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.models.community_check import CommunityCheck
from citizen_connect_app.models.utils import Location
from citizen_connect_app.utils.commons import (resolve_location , update_user_category_statistics)
from citizen_connect_app.utils.error_logger import ErrorLogger


logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50,
)




def create(community_check_data: dict) -> Result:
    try:
        try:
            community_check = CommunityCheck(**community_check_data)
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
            return Result.bad_request(message="; ".join(messages))

        saved_files = []
        for file in community_check.files:
            saved_file = frappe.get_doc({
                "doctype": "File",
                "file_name": file.filename,
                "content": file.read(),
                "is_private": 1,
            }).insert(ignore_permissions=True)
            saved_files.append({
                "doctype": "Media",
                "media": saved_file.file_url
            })

        location = Location()

        if community_check.location:
            location_result = resolve_location(community_check.location)

            if location_result.is_bad_request:
                return location_result

            location.country = location_result.data.country
            location.geo1 = location_result.data.geo1
            location.geo2 = location_result.data.geo2

        user_id = None

        if frappe.session.user != "Guest":
            user_id = frappe.session.user
        elif community_check.user_id:
            user_id = community_check.user_id

        doc_data = {
            "doctype": "Case",
            "type": "Community Check",
            "user_id": user_id,
            "title":community_check.title,
            "description":community_check.description,
            "category":"Infra Maintenance",
            "water_supply": community_check.water_supply,
            "electricity": community_check.electricity,
            "road": community_check.road,
            "teacher_at_school": community_check.teacher_at_school,
            "healthcare": community_check.healthcare,
            "internet": community_check.internet,
            "sanitation": community_check.sanitation,
            "local_governance": community_check.local_governance,
            "confidence_level": community_check.confidence_level,
            "country": location.country,
            "geo_l1": location.geo1,
            "geo_l2": location.geo2,
            "media":saved_files
        }
        frappe.get_doc(doc_data).insert(ignore_permissions=True)
        if user_id:
            update_user_category_statistics(
                user_id,
                "Infra Maintenance"
            )

        return Result.success(
            message="Community check created successfully.",
        
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to create community check.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )
def count_community(user_id: str) -> Result:
        community_count = frappe.db.count(
             "Case",
            {
               "user_id": user_id,
               "type": "Community Check",
            }
             )

        return Result.success(
             message="Community Check count fetched successfully.",
             data=community_count,
             )
def get_user_community_check(user_id: str) -> Result:
    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        community_checks = frappe.db.get_all(
            "Case",
            filters={
                "user_id": user_id,
                "type": "Community Check",
            },
            fields=[
                "geo_l1",
                "geo_l2",
                "workflow_state",
            ],
            order_by="creation desc",
        )

        data = []

        for check in community_checks:
            location = None

            if check.geo_l2:
                location = frappe.db.get_value(
                    "Geography L2",
                    check.geo_l2,
                    "geo_l2"
                )

            if not location and check.geo_l1:
                location = frappe.db.get_value(
                    "Geography L1",
                    check.geo_l1,
                    "geo_l1"
                )

            data.append({
                "title":f"Community Check in {location}",
                "workflow_state": check.workflow_state,
            })

        return Result.success(
            message="Community Check data fetched successfully.",
            data=data,
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch Community Check data.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )