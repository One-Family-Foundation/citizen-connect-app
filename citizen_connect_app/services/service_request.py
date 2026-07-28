import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class ServiceRequestManager:

    @staticmethod
    def create(data: dict, attachment=None) -> Result:
        try:
            if not data.get("mobile_num"):
                return Result.bad_request("Mobile Number is required")

            if not data.get("service_name"):
                return Result.bad_request("Service Name is required")

            # Check if the user has already requested this service
            if frappe.db.exists(
                "Service Request Help",
                {
                    "mobile_num": data.get("mobile_num"),
                    "service_name": data.get("service_name"),
                },
            ):
                return Result.bad_request(
                    "You have already submitted a request for this service."
                )

            service_request = frappe.new_doc("Service Request Help")
            service_request.service_name = data.get("service_name")
            service_request.full_name = data.get("full_name")
            service_request.mobile_num = data.get("mobile_num")
            service_request.age = data.get("age")
            service_request.gender = data.get("gender")
            service_request.situation_desc = data.get("situation_desc")

            if attachment:
                file_doc = frappe.get_doc({
                    "doctype": "File",
                    "file_name": attachment.filename,
                    "content": attachment.stream.read(),
                    "is_private": 0,
                })
                file_doc.save(ignore_permissions=True)
                service_request.attachment = file_doc.file_url
            service_request.save(ignore_permissions=True)

            return Result.success(
                "Service request submitted successfully",
                data={
                    "name": service_request.name,
                    "status": "New",
                },
            )

        except Exception as e:
            ErrorLogger.log(e)
            
            return Result.failure(
                "Failed to create service request",
                error_data=str(e),
            )

   