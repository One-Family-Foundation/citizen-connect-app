import frappe

from citizen_connect_app.services.community_check_manager import (
    get_user_community_check
)
from citizen_connect_app.services.issue_manager import get_user_issue_list
from citizen_connect_app.services.request_help import RequestHelpManager
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0

@staticmethod
def get_user_case_list(
    user_id: str,
    status: str = "All",
    limit=DEFAULT_LIMIT,
    offset=DEFAULT_OFFSET,
) -> Result:

    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        allowed_statuses = [
            "Open",
            "In Progress",
            "Closed",
            "Resolved"
        ]

        if status != "All" and status not in allowed_statuses:
            return Result.bad_request(
                message="Invalid status. Allowed values are All, Open, In Progress, Closed, Resolved."
            )

        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))

        requests = RequestHelpManager.get_user_request_list(user_id)
        issues = get_user_issue_list(user_id)
        community_checks = get_user_community_check(user_id)

        data = []

        if requests.success:
            data.extend(requests.data)

        if issues.success:
            data.extend(issues.data)

        if community_checks.success:
            data.extend(community_checks.data)

        # Filter by workflow state
        if status != "All":
            data = [
                item for item in data
                if item.get("workflow_state") == status
            ]

        
       
        paginated_data = data[offset : offset + limit]

        return Result.success(
            message="User request list fetched successfully.",
            data={
                "requests": paginated_data
            }
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch user request list.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()}
        )

