import frappe
from frappe import _
from pydantic import ValidationError

from citizen_connect_app.models.user import User
from citizen_connect_app.services.otp_service import OTPService
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger


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
        location = user_data.location
        
        geo_l1 = None
        geo_l2 = None
        if location:
            geo_l1 = frappe.db.get_value(
              "Geography L1",
              {"geo_l1": location.geo1},
               "name",
            )
            geo_l2 = frappe.db.get_value(
               "Geography L2",
               {"geo_2": location.geo2},
                "name",
            )
        try:
            # Create User
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": user_data.email,
                    "first_name": user_data.full_name,
                    "mobile_no": user_data.mobile_no,
                    "enabled": 1,
                    "send_welcome_email": 0,
                }
            )
            user.insert(ignore_permissions=True)

            # Create User Profile
            user_profile = frappe.get_doc(
                {
                    "doctype": "User Profile",
                    "user": user.name,
                    "phone": user_data.mobile_no,
                    "user_type": "Citizen",
                    "country":location.country if location else None,
                    "geo_l1": geo_l1,
                    "geo_l2": geo_l2,
                }
            )
            user_profile.insert(ignore_permissions=True)

            # Commit only if both inserts succeed
            frappe.db.commit()

            # Login user
            frappe.local.login_manager.user = user.name
            frappe.local.login_manager.post_login()

            # Clear OTP verification
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

        except Exception as e:
            # Rollback User if User Profile creation fails
            frappe.db.rollback()

            ErrorLogger.log(e)
            return Result.failure(
                message="Registration failed. Please check your location details and try again."
            )

    @staticmethod
    def login(email, otp):
        email = (email or "").strip().lower()

        try:
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

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                message=str(e)
            )