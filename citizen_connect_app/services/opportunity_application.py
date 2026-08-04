import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class OpportunityApplicationManager:

    @staticmethod
    def create(data: dict, attachment=None) -> Result:
        try:
            if not data.get("opportunity_id"):
                return Result.bad_request("Opportunity ID is required")

            if not data.get("email"):
                return Result.bad_request("Email is required")

            # Prevent same user from applying twice
            filters = {
                "opportunity_id": data.get("opportunity_id"),
                "email": data.get("email"),
            }

            if frappe.db.exists("Opportunity Form", filters):
                return Result.bad_request(
                    "You have already submitted an application for this opportunity."
                )

            application = frappe.new_doc("Opportunity Form")

            application.opportunity_id = data.get("opportunity_id")
            application.full_name = data.get("full_name")
            application.email = data.get("email")
            application.phone = data.get("phone")
            application.age = data.get("age")
            application.gender = data.get("gender")
            application.description = data.get("description")

            # Save attachment if provided
            if attachment:
                file_doc = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": attachment.filename,
                        "content": attachment.stream.read(),
                        "is_private": 0,
                    }
                )
                file_doc.save(ignore_permissions=True)
                application.attachment = file_doc.file_url

            application.save(ignore_permissions=True)

            return Result.success(
                "Application submitted successfully",
                data={
                    "name": application.name,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                "Failed to submit application",
                error_data=str(e),
            )