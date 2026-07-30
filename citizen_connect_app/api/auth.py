import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.authmanager import UserManager
from citizen_connect_app.utils.error_logger import ErrorLogger


@frappe.whitelist(allow_guest=True)
def register(full_name, email, mobile_no):
    try:
        data = UserManager.register(
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
        )

        return custom_response(
            message="Registration successful. OTP sent (check server console).",
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
def verify_registration_otp(email, otp):
    try:
        data = UserManager.verify_registration_otp(
            email=email,
            otp=otp,
        )

        return custom_response(
            message="Account verified successfully.",
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
def resend_otp(email, purpose="Registration"):
    try:
        data = UserManager.resend_otp(
            email=email,
            purpose=purpose,
        )

        return custom_response(
            message="OTP resent (check server console).",
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
def login(email):
    try:
        data = UserManager.login_request_otp(email=email)

        return custom_response(
            message="OTP sent for login (check server console).",
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
def verify_login_otp(email, otp):
    try:
        data = UserManager.login_verify_otp(
            email=email,
            otp=otp,
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