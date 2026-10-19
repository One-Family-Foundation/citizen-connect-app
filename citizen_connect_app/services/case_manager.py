from psycopg2.extensions import Int
import frappe
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result
from citizen_connect_app.utils.commons import (update_user_category_statistics)
from citizen_connect_app.services.community_check_manager import (create as create_community_check,)
from citizen_connect_app.services.issue_manager import ( create as create_issue,)
from citizen_connect_app.services.request_help import RequestHelpManager

MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0


def community_check(community_check_data:dict)->Result:
    return create_community_check(community_check_data)

def issue(issue_data:dict)->Result:
    return create_issue(issue_data)

def create_help_request(request_data, request_type, attachment=None)->Result:
    return RequestHelpManager.create(
        request_data=request_data,
        request_type=request_type,
        attachment=attachment,
    )


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
            "Resolved",
        ]

        if status != "All" and status not in allowed_statuses:
            return Result.bad_request(
                message=(
                    "Invalid status. Allowed values are "
                    "All, Open, In Progress, Closed, Resolved."
                )
            )

        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))

        cases = frappe.db.sql(
            """
            SELECT
                c.type,
                c.title,
                c.workflow_state,
                CASE
                    WHEN c.workflow_state = 'Resolved'
                    THEN c.case_summary
                    ELSE NULL
                END AS case_summary,    
                c.geo_l1,
                c.geo_l2,
                c.scheme_id,
                c.service_id
            FROM `tabCase` c
            WHERE c.user_id = %s
            ORDER BY c.creation DESC
            """,
            (user_id,),
            as_dict=True,
        )

        data = []

        for case in cases:
           
            # Issue
            if case.type == "Issue":
                item= {
                    "title": case.title,
                    "workflow_state": case.workflow_state,
                }
                if case.workflow_state == "Resolved":
                    item["case_summary"] = case.case_summary  

                data.append(item)
            # Scheme Request
                
            elif case.type == "Scheme Request":
                scheme_name = None

                if case.scheme_id:
                    scheme_name = frappe.db.get_value(
                        "Scheme",
                        case.scheme_id,
                        "scheme_name",
                    )

                item={
                    "title":( 
                        f"Scheme Request in {scheme_name}"
                        if scheme_name
                        else "Scheme Request"
                    ),
                    "workflow_state": case.workflow_state,
                }
                if case.workflow_state == "Resolved":
                    item["case_summary"] = case.case_summary
                data.append(item)    

            # Service Request
            elif case.type == "Service Request":
                service_title = None

                if case.service_id:
                    service_title = frappe.db.get_value(
                        "Service",
                        case.service_id,
                        "title",
                    )

                item={
                    "title": f"Service Request in {service_title}"
                    if service_title
                    else "Service Request",
                    "workflow_state": case.workflow_state,
                }
                if case.workflow_state == "Resolved":
                    item["case_summary"] = case.case_summary
                data.append(item)
            # Community Check
            elif case.type == "Community Check":
                location = None

                if case.geo_l2:
                    location = frappe.db.get_value(
                        "Geography L2",
                        case.geo_l2,
                        "geo_l2",
                    )

                if not location and case.geo_l1:
                    location = frappe.db.get_value(
                        "Geography L1",
                        case.geo_l1,
                        "geo_l1",
                    )

                data.append({
                    "title": (
                        f"Community Check in {location}"
                        if location
                        else "Community Check"
                    ),
                    "workflow_state": case.workflow_state,
                })

        # Filter by workflow state
        if status != "All":
            data = [
                item
                for item in data
                if item.get("workflow_state") == status
            ]

        # Pagination
        paginated_data = data[offset:offset + limit]

        return Result.success(
            message="User case list fetched successfully.",
            data={
                "requests": paginated_data,
                "total": len(data),
            },
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch user case list.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback()
            },
        )

def get_user_case_count(user_id:str)->Int:
    return frappe.db.count(
        "Case",
       filters= {
            "user_id":user_id,
            "type" : ["in", ["Issue", "Community Check" ,"Scheme Request" ,"Service Request"]]
        }
      )
   
def get_case_resolved_count(user_id:str)->Int:
    return frappe.db.count(
        "Case",
        filters = {
            "user_id":user_id,
            "workflow_state": "Resolved",
            "type": ["in", ["Issue", "Community Check" ,"Scheme Request" ,"Service Request"]],
        }
    )

def on_trash(doc) ->Result:
    user_id = doc.user
    category_l1 = doc.category_l1
    
    update_user_category_statistics(
        user_id,
        category_l1,
        is_deleted=True
    )
 
