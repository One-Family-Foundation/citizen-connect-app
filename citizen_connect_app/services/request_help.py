import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class RequestHelpManager:

    @staticmethod
    def create(data: dict, request_type: str, attachment=None) -> Result:
        try:
            if not data.get("mobile_num"):
                return Result.bad_request("Mobile Number is required")

            filters = {
                "mobile_num": data.get("mobile_num"),
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
            request.full_name = data.get("full_name")
            request.email = data.get("email")
            request.mobile_num = data.get("mobile_num")
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