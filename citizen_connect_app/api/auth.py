import frappe

from samaaja.utils.custom_response import custom_response
from samaaja.utils.result import Result

from citizen_connect_app.services.otp_service import OTPService
from citizen_connect_app.services.user import UserManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def send_otp(email):
    try:
        result = OTPService.send_otp(email=email)

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(message="Something went wrong.",
            error_data=str(e),).to_custom_response( )


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    try:
        result = OTPService.verify_otp(email=email, otp=otp)

        return result.to_custom_response( )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Something went wrong.",
            error_data=str(e),
            ).to_custom_response()


@frappe.whitelist(allow_guest=True)
def login(email, otp):
    try:
        result = UserManager.login(
            email=email,
            otp=otp,
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            error_data=str(e),
        ).to_custom_response()


@frappe.whitelist(allow_guest=True)
def register(full_name, email, mobile_no=None, location=None):
    try:
        result = UserManager.register(
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
            location=location,
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            error_data=str(e),
        ).to_custom_response()