import frappe
from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.models.report_issue import ReportIssue
from citizen_connect_app.models.utils import Location
from citizen_connect_app.utils.commons import resolve_location
from citizen_connect_app.utils.error_logger import ErrorLogger


logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50,
)

logger.setLevel("DEBUG")


def create_report(report_data: dict) -> Result:
    try:
        try:
            report = ReportIssue(**report_data)
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
            return Result.bad_request(message="; ".join(messages))

        media_url = None

        file = frappe.request.files.get("file")

        if "file" in file.filename:
            saved_file = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": file.filename,
                    "content": file.read(),
                    "is_private": 1,
                }
            ).insert(ignore_permissions=True)

            media_url = saved_file.file_url

        location = Location()

        if report.location:
            location_result = resolve_location(report.location)

            if location_result.is_bad_request:
                return location_result

            location.country = location_result.data.country
            location.geo1 = location_result.data.geo1
            location.geo2 = location_result.data.geo2

        user_id = None

        if frappe.session.user != "Guest":
            user_id = frappe.session.user
        elif report.user_id:
            user_id = report.user_id

        doc_data = {  
               "doctype": "Report Issue",
                "user_id": user_id,
                "issue_category": report.category.l1 if report.category else None,
                "urgency": report.urgency,
                "description": report.description,
                "country": location.country,
                "geo_l1": location.geo1,
                "geo_l2": location.geo2,
                "allow_contact": report.allow_contact,
             }
        if media_url:
            doc_data["media"] = media_url

        doc = frappe.get_doc(doc_data).insert(ignore_permissions=True)    

        logger.info(f"Report Issue created with ID: {doc.name}")

        return Result.success(
            message="Report issue created successfully.",
            data=doc.as_dict(),
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to create report issue.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )