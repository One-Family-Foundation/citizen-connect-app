import frappe

from citizen_connect_app.models.request_help import RequestHelp
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class RequestHelpManager:

    @staticmethod
    def create(request_data: dict, request_type: str, attachment=None) -> Result:
        try:
            if frappe.session.user == "Guest":
                request_help = RequestHelp(**request_data)

                if not request_help.full_name or not request_help.email_id:
                    return Result.bad_request("fullname and email are mandatory")

                full_name = request_help.full_name
                email = request_help.email_id
                mobile_num = request_help.mobile_num
                user_id = None
                

            else:
                user = frappe.get_doc("User", frappe.session.user)

                profile_name = frappe.db.get_value(
                    "User Profile",
                    {"user": user.name},
                    "name"
                )

                if not profile_name:
                    return Result.bad_request("Profile not found")

                profile = frappe.get_doc(
                    "User Profile",
                    profile_name
                )

                request_data["full_name"] = user.first_name
                request_data["email_id"] = user.email

                if profile.phone:
                    request_data["mobile_num"] = profile.phone

                request_help = RequestHelp(**request_data)

                full_name = request_help.full_name
                email = request_help.email_id
                mobile_num = request_help.mobile_num
                user_id = user.name

                if not profile.phone:
                    profile.phone = mobile_num
                    profile.save(ignore_permissions=True)

            if request_type == "service":
                if not request_help.service_name:
                    return Result.bad_request(
                        "Service Name is required"
                    )

                case_type = "Service Request"


            elif request_type == "scheme":
                if not request_help.scheme_name:
                    return Result.bad_request(
                        "Scheme Name is required"
                    )

                case_type = "Scheme Request"        

            else:
                return Result.bad_request(
                    "Invalid request type"
                )

            case = frappe.new_doc("Case")

            case.type = case_type
            case.user_id = user_id
            case.user_name = full_name
            case.email_id = email
            case.mobile_no = mobile_num
            case.age = request_help.age
            case.gender = request_help.gender
            case.description = request_help.description
            
            if request_type == "service":
                case.service_id = request_help.service_name
                case.category = frappe.db.get_value(
                    "Service",
                     request_help.service_name,
                     "category_l1"
                )
            else:
                case.scheme_id = request_help.scheme_name
                case.category = frappe.db.get_value(
                    "Scheme",
                    request_help.scheme_name,
                    "category_l1"
                )

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

                case.append(
                    "media",
                    {
                        "media": file_doc.file_url
                    }
                )

            case.save(ignore_permissions=True)

            return Result.success(
                "Request submitted successfully",
                data={
                    "name": case.name,
                    "status": "New",
                },
            )

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                "Failed to create request",
                error_data=str(e),
            )

    