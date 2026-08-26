import frappe

from citizen_connect_app.models.volunteer_opportunity import (
    GuestOpportunityForm,
    LoggedInOpportunityForm,
)
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class OpportunityApplicationManager:

    @staticmethod
    def create(data: dict, attachment=None) -> Result:
        try:
            if frappe.session.user == "Guest":
                data = GuestOpportunityForm(**data)

                full_name = data.full_name
                email = data.email
                phone = data.phone
                user = None

            else:
                data = LoggedInOpportunityForm(**data)

                user = frappe.get_doc("User", frappe.session.user)

                profile_name = frappe.db.get_value(
                    "User Profile",
                    {"user": user.name},
                    "name",
                )

                if not profile_name:
                    return Result.not_found("User profile not found.")

                profile = frappe.get_doc("User Profile", profile_name)

                full_name = user.first_name
                email = user.email

                if profile.phone:
                    phone = profile.phone
                else:
                    if not data.phone:
                        return Result.bad_request(
                            "Phone number is required."
                        )

                    phone = data.phone
                    profile.phone = phone
                    profile.save(ignore_permissions=True)

            opportunity = frappe.db.get_value(
                    "Opportunity Discovery",
                     {
                         "name": data.opportunity_id,
                         "status": "Active",
                     },
                     ["name", "category_l1"],
                     as_dict=True,
            )
            if not opportunity:
                return Result.not_found("Volunteer opportunity not found.")

            if frappe.session.user == "Guest":
                duplicate = frappe.db.exists(
                    "Opportunity Form",
                    {
                        "opportunity_id": data.opportunity_id,
                        "email": email,
                    },
                )
            else:
                duplicate = frappe.db.exists(
                    "Opportunity Form",
                    {
                        "opportunity_id": data.opportunity_id,
                        "user": user.name,
                    },
                )

            if duplicate:
                return Result.bad_request(
                    "You have already submitted an application for this opportunity."
                )

            application = frappe.new_doc("Opportunity Form")

            application.opportunity_id = data.opportunity_id

            if frappe.session.user != "Guest":
                application.user = user.name

            application.full_name = full_name
            application.email = email
            application.phone = phone
            application.age = data.age
            application.gender = data.gender
            application.description = data.description

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
                message="Application submitted successfully.",
                data={
                    "name": application.name,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                message="Failed to submit application.",
                error_data=str(e),
            )