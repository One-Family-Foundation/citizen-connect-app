import frappe

from frappe import user
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.models.volunteer_action_model import (
    VolunteerAction
)
from citizen_connect_app.models.utils import Location
from pydantic import ValidationError
from citizen_connect_app.utils.commons import (
    resolve_location
)
from citizen_connect_app.services.user import UserManager
from citizen_connect_app.utils.commons import update_user_category_statistics

logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50
)

logger.setLevel("DEBUG")

MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0

def create_volunteer_action(volunteer_action_data: dict) -> Result:
    try:
        if frappe.session.user == "Guest":
            return Result.bad_request(
                message="User must be logged in to create a volunteer action."
            )

        try:
            volunteer_action = VolunteerAction(**volunteer_action_data)
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]

            return Result.bad_request(
                message="; ".join(messages)
            )

        # Resolve location
        location = Location()

        if volunteer_action.location:
            location_result = resolve_location(
                volunteer_action.location
            )

            if location_result.is_bad_request:
                return location_result

            location.country = location_result.data.country
            location.geo1 = location_result.data.geo1
            location.geo2 = location_result.data.geo2

        # Save media
        saved_files = []

        for file in volunteer_action.media:
            saved_file = frappe.get_doc({
                "doctype": "File",
                "file_name": file.filename,
                "content": file.read(),
                "is_private": 0,
            }).insert(ignore_permissions=True)

            saved_files.append({
                "doctype": "Media",
                "media": saved_file.file_url
            })

        # Create Volunteer Action
        doc = frappe.get_doc({
            "doctype": "Volunteer Action",
            "user": frappe.session.user,
            "category_l1": volunteer_action.category.l1,
            "description": volunteer_action.description,
            "start_date": volunteer_action.start_date,
            "end_date": volunteer_action.end_date,
            "country": location.country,
            "geo_l1": location.geo1,
            "geo_l2": location.geo2,
            "media": saved_files,
        }).insert(ignore_permissions=True)

        logger.info(
            f"Volunteer Action created with ID: {doc.name}"
        )
        on_create(doc)
        return Result.success(
            message="Volunteer action created successfully.",
            data=doc.as_dict()
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to create volunteer action.",
            data={
                "error": str(e)
            },
            error_data={
                "traceback": frappe.get_traceback()
            }
        )

def get_user_actions(
    user_id: str,
    limit=DEFAULT_LIMIT,
    offset=DEFAULT_OFFSET,
) -> Result:
    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))

        # Volunteer Actions
        volunteer_actions = frappe.get_all(
            "Volunteer Action",
            filters={
                "user": user_id,
            },
            fields=[
                "description",
                "creation",
            ],
            order_by="creation DESC",
        )

        # Community Check + Report Issue
        cases = frappe.get_all(
            "Case",
            filters={
                "user_id": user_id,
                "type": ["in", ["Community Check", "Issue"]],
            },
            fields=[
                "type",
                "description",
                "creation",
            ],
            order_by="creation DESC",
        )

        community_checks = []
        report_issues = []

        for case in cases:
            item = {
                "description": case.description,
                "creation": case.creation,
            }

            if case.type == "Community Check":
                community_checks.append(item)

            elif case.type == "Issue":
                report_issues.append(item)

        # Combine all actions
        actions = volunteer_actions + community_checks + report_issues

        # Latest first
        actions.sort(
            key=lambda x: x.get("creation"),
            reverse=True,
        )

        # Counts
        volunteer_action_count = len(volunteer_actions)
        community_check_count = len(community_checks)
        report_issue_count = len(report_issues)
        total = len(actions)

        # Pagination
        paginated_actions = actions[
            offset:offset + limit
        ]

        return Result.success(
            message="User actions fetched successfully.",
            data={
                "actions": paginated_actions,
                "counts": {
                    "volunteer_action": volunteer_action_count,
                    "community_check": community_check_count,
                    "report_issue": report_issue_count,
                    "total": total,
                },
            },
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to get user actions.",
            data={
                "error": str(e),
            },
        )

def on_create(doc) -> Result:
    user_id = doc.user
    category_l1 = doc.category_l1

    update_user_category_statistics(
        user_id,
        category_l1,
        is_deleted=False
    )
def on_trash(doc) ->Result:
    user_id = doc.user
    category_l1 = doc.category_l1
    
    update_user_category_statistics(
        user_id,
        category_l1,
        is_deleted=True
    )