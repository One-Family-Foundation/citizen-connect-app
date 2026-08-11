import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class RequestHelpManager:

    @staticmethod
    def create(data: dict, request_type: str, attachment=None) -> Result:
        try:
            if frappe.session.user == "Guest":
                full_name = data.get("full_name")
                email = data.get("email")
                mobile_num = data.get("mobile_num")
            else:
                user = frappe.get_doc("User",  frappe.session.user)
                profile_name = frappe.db.get_value("User Profile", {"user":user.name},"name")
                if not profile_name:
                    return Result.bad_request("Profile not found")
                profile = frappe.get_doc("User Profile", profile_name)
                full_name = user.first_name
                email = user.email

                if profile.phone:
                    mobile_num = profile.phone
                else:
                    if not data.get("mobile_num"):
                        return Result.bad_request("mobile number is required")
                    mobile_num = data.get("mobile_num")
                    profile.phone = mobile_num
                    profile.save(ignore_permissions=True)                   
        
            

            filters = {
                "mobile_num": mobile_num
            }

            if request_type == "service":
                if not data.get("service_name"):
                    return Result.bad_request("Service Name is required")

                filters["service_name"] = data.get("service_name")

            elif request_type == "scheme":
                if not data.get("scheme_name"):
                    return Result.bad_request("Scheme Name is required")

                filters["scheme_name"] = data.get("scheme_name")

            if frappe.db.exists("Request Help", filters):
                return Result.bad_request(
                    f"You have already submitted a request for this {request_type}."
                )

            request = frappe.new_doc("Request Help")

            request.service_name = data.get("service_name")
            request.scheme_name = data.get("scheme_name")
            request.full_name = full_name
            request.email = email
            request.mobile_num = mobile_num
            request.age = data.get("age")
            request.gender = data.get("gender")
            request.situation_desc = data.get("situation_desc")

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
                request.attachment = file_doc.file_url

            request.save(ignore_permissions=True)

            return Result.success(
                "Request submitted successfully",
                data={
                    "name": request.name,
                    "status": "New",
                },
            )

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                "Failed to create request",
                error_data=str(e),
            )