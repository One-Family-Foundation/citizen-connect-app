import json
import frappe
from frappe.utils.oauth import get_oauth2_authorize_url
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
        return custom_response(
            message="Something went wrong.",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    try:
        result = OTPService.verify_otp(email=email, otp=otp)
        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )


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
        return custom_response(
            message="Something went wrong.",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def register(full_name, email, mobile_no=None, location=None):
    try:
        if isinstance(location, str) and location.strip():
            try:
                location = json.loads(location)
            except (ValueError, TypeError):
                location = None

        result = UserManager.register(
            full_name=full_name,
            email=email,
            mobile_no=mobile_no,
            location=location,
        )
        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def get_google_auth_url():
    """
    Generate Google OAuth authorization URL.
    """
    provider = "google"

    try:
        auth_url = get_oauth2_authorize_url(
            provider,
            redirect_to="/homepage"
        )

        return Result.success(
            message="Google authentication URL generated successfully.",
            data={"auth_url": auth_url},
        ).to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)
        return custom_response(
            message="Something went wrong.",
            data={"error": str(e)},
            status_code=500,
            error=True,
        )