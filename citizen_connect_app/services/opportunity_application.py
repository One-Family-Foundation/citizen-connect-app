import frappe

from citizen_connect_app.models.volunteer_opportunity import (
    GuestOpportunityForm,
    LoggedInOpportunityForm,
)
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result
from citizen_connect_app.utils.commons import update_user_category_statistics


class OpportunityApplicationManager:

    @staticmethod
    def create(data: dict, attachment=None) -> Result:
        try:
            if frappe.session.user == "Guest":
                data = GuestOpportunityForm(**data)
                if not data.full_name:
                   return Result.bad_request("Full name is required.")

                if not data.email:
                   return Result.bad_request("Email is required.")

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
            frappe.db.commit()
            if user and opportunity.category_l1:
                update_user_category_statistics(
                   user.name,
                   opportunity.category_l1
                )
        
        
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
def count_volunteer_actions(user_id: str) -> Result:
    opportunity_actions = frappe.db.count(
        "Opportunity Form",
        {
            "user": user_id,
        },
    )

    return Result.success(
        message="Volunteer action count fetched successfully.",
        data=opportunity_actions,
    )
def get_volunteer_actions(user_id: str) -> Result:
    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        opportunities = frappe.db.sql(
            """
            SELECT
                of.name AS application_id,
                of.opportunity_id,
                od.title,
                od.category_l1,
                od.category_l2,
                od.status,
                of.creation
            FROM `tabOpportunity Form` of
            INNER JOIN `tabOpportunity Discovery` od
                ON od.name = of.opportunity_id
            WHERE of.user = %s
            ORDER BY of.creation DESC
            """,
            (user_id,),
            as_dict=True,
        )

        return Result.success(
            message="User volunteer participation fetched successfully.",
            data=opportunities,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to fetch user volunteer participation.",
            error_data=str(e),
        )