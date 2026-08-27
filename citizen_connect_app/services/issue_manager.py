import frappe
from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.models.issue import Issue
from citizen_connect_app.models.utils import Location
from citizen_connect_app.utils.commons import resolve_location  
from citizen_connect_app.utils.error_logger import ErrorLogger


logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50,
)

logger.setLevel("DEBUG")


def create(issue_data: dict) -> Result:
    try:
        try:
            issue = Issue(**issue_data)
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
            return Result.bad_request(message="; ".join(messages))

        saved_files = []
        for file in issue.files:
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

        if issue.location:
            location_result = resolve_location(issue.location)

            if location_result.is_bad_request:
                return location_result

            location.country = location_result.data.country
            location.geo1 = location_result.data.geo1
            location.geo2 = location_result.data.geo2

        user_id = None

        if frappe.session.user != "Guest":
            user_id = frappe.session.user
        elif issue.user_id:
            user_id = issue.user_id

        doc_data = {  
               "doctype": "Case",
               "type": "Issue",
               "title":issue.title,
                "user_id": user_id,
                "category": issue.category.l1 if issue.category else None,
                "urgency": issue.urgency,
                "description": issue.description,
                "country": location.country,
                "geo_l1": location.geo1,
                "geo_l2": location.geo2,
                "allow_contact": issue.allow_contact,
                "media": saved_files,
             }

        doc = frappe.get_doc(doc_data).insert(ignore_permissions=True)
        
      
        response_data = {
            "name": doc.name,
            "title": doc.title,
            "description": doc.description,
            "type": doc.type,
            "urgency": doc.urgency,
            "category": doc.category,
            "location": {
                "country": doc.country,
                "geo_l1": doc.geo_l1,
                "geo_l2": doc.geo_l2,
             },
            "media": [
               {
                   "media": item.media
                }
                for item in doc.media
            ],
    }

        logger.info(f"Issue created with ID: {doc.name}")

        return Result.success(
            message="Issue created successfully.",
            data=response_data,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to create issue.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )