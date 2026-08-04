import frappe
from frappe import _
from pydantic import ValidationError

from citizen_connect_app.models.user import User
from citizen_connect_app.services.otp_service import OTPService
from samaaja.utils.result import Result


class UserManager:
    
    @staticmethod
    def register(full_name, email, mobile_no, location):
        email = (email or "").strip().lower()

        if not OTPService.is_verified(email):
            return Result.bad_request(
                message="Please verify your email with an OTP before registering."
            )
        try:
            user_data = User(
                full_name=full_name,
                email=email,
                mobile_no=mobile_no,
                location=location,
            )
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
            return Result.bad_request(message="; ".join(messages))

        if frappe.db.exists("User", {"email": user_data.email}):
            return Result.bad_request(message="Email already registered.")

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": user_data.email,
                "first_name": user_data.full_name,
                "mobile_no": user_data.mobile_no,
                "location": user_data.location,
                "enabled": 1,
                "send_welcome_email": 0,
            }
        )
        user.insert(ignore_permissions=True)

        frappe.local.login_manager.user = user.name
        frappe.local.login_manager.post_login()

        OTPService.clear_verified(email)

        return Result.success(
            message="User registered successfully.",
            data={
                "user_id": user.name,
                "full_name": user.full_name,
                "email": user.email,
                "mobile_no": user.mobile_no,
                "sid": frappe.session.sid,
            },
        )

    @staticmethod
    def login(email, otp):
        email = (email or "").strip().lower()

        otp_result = OTPService.verify_otp(email, otp)

        if not otp_result.success:
            return otp_result

        user_name = frappe.db.get_value("User", {"email": email}, "name")
        if not user_name:
            return Result.not_found(message="User not found.")

        frappe.local.login_manager.user = user_name
        frappe.local.login_manager.post_login()

        return Result.success(
            message="Login successful.",
            data={
                "user_id": user_name,
                "sid": frappe.session.sid,
            },
        )