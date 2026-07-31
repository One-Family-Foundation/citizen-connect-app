import frappe
from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.otp_service import OTPService
from citizen_connect_app.services.user import UserManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def send_otp(email):
    try:
        data = OTPService.send_otp(email=email)

        return custom_response(
            message="OTP sent (check server console).",
            data=data,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            status_code=400 if isinstance(e, frappe.ValidationError) else 500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    try:
        verified = OTPService.verify_otp(email=email, otp=otp)

        return custom_response(
            message="OTP verified." if verified else "Invalid or expired OTP.",
            data={"verified": verified},
        )

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            status_code=400 if isinstance(e, frappe.ValidationError) else 500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def login(email, otp):
    try:
        data = UserManager.login(email=email, otp=otp)

        if not data.get("success"):
            return custom_response(
                message=data.get("message", "Login failed."),
                status_code=400,
                error=True,
            )

        return custom_response(
            message="Login successful.",
            data=data,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            status_code=400 if isinstance(e, frappe.ValidationError) else 500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def register(full_name, email, mobile_no=None,  location=None):
    try:
        data = UserManager.register(
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
            location = location
        )

        if isinstance(data, dict) and data.get("success") is False:
            return custom_response(
                message=data.get("message", "Registration failed."),
                status_code=400,
                error=True,
            )


        return custom_response(
            message="Registration successful.",
            data=data,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message=str(e) if isinstance(e, frappe.ValidationError) else "Something went wrong.",
            status_code=400 if isinstance(e, frappe.ValidationError) else 500,
            error=True,
        )