import frappe
from frappe import _
from pydantic import ValidationError
from urllib.parse import quote
from citizen_connect_app.models.user import User
from citizen_connect_app.services.otp_service import OTPService
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.models.user import UserSummary
from citizen_connect_app.models.utils import Location
from citizen_connect_app.models.utils import MediaResponse

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
        
        country = None
        geo_l1 = None
        geo_l2 = None
        if user_data.location:
            location = user_data.location
            if location.country:
                country = frappe.db.get_value(
                    "Country",
                    {"country_name": location.country},
                    "name"
                )
                if not country:
                    return Result.bad_request(
                        message="Invalid country selected."
                )
                if location.geo1:
                    geo_l1 = frappe.db.get_value(
                        "Geography L1",
                        {"geo_l1": location.geo1},
                        "name"
                    )
                    if not geo_l1:
                        return Result.bad_request(
                        message="Invalid Geography L1 selected."
                    )
                    if location.geo2:
                        geo_l2 = frappe.db.get_value(
                            "Geography L2",
                            {"geo_l2": location.geo2},
                            "name"
                        )
                    if not geo_l2:
                        return Result.bad_request(
                            message="Invalid Geography L2 selected."
                        )
        try:
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": user_data.email,
                    "first_name": user_data.full_name,
                    "enabled": 1,
                    "send_welcome_email": 0,
                }
            )
            user.insert(ignore_permissions=True)

            user_profile = frappe.get_doc(
                {
                    "doctype": "User Profile",
                    "user": user.name,
                    "phone": user_data.mobile_no,
                    "user_type": "Citizen",
                    "country": country if location else None,
                    "geo_l1": geo_l1 if location else None,
                    "geo_l2": geo_l2 if location else None,
                }
            )
            user_profile.insert(ignore_permissions=True)

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
            ErrorLogger.log(e)
            return Result.failure(
                message="Registration failed. Please check your location details and try again."
            )


    @staticmethod
    def get_user_summaries(
        emails: list[str],
        lang: str | None = None,
    ) -> list[UserSummary]:
        try:
            emails = list({
                email.strip().lower()
                for email in emails
                if email
            })

            if not emails:
                return []

            users = frappe.db.get_all(
                "User",
                filters={"name": ["in", emails]},
                fields=["name", "full_name", "user_image"],
            )

            profiles = frappe.db.get_all(
                "User Profile",
                filters={"user": ["in", emails]},
                fields=["user", "user_type", "country", "geo_l1", "geo_l2"],
            )

            users_by_email = {
                user.name: user
                for user in users
            }

            profiles_by_email = {
                profile.user: profile
                for profile in profiles
            }

            media_base_url = frappe.utils.get_url().rstrip("/")

            user_summaries = []

            for email in emails:
                user = users_by_email.get(email)

                if not user:
                    continue

                profile = profiles_by_email.get(email)

                media_url = user.user_image

                
                if media_url and not media_url.startswith(("http://", "https://")):
                    media_url = f"{media_base_url}/{quote(media_url.lstrip('/'), safe='/')}"

                user_summaries.append(
                    UserSummary(
                        full_name=user.full_name,
                        email=user.name,
                        location={
                            "country": {
                                "name": profile.country if profile else None
                            },
                            "geo1": {
                                "name": profile.geo_l1 if profile.geo_l1 else None
                            },
                            "geo2": {
                                "name": profile.geo_l2 if profile.geo_l2 else None
                            }
                        },
                        type=profile.user_type if profile else None,
                        profile_picture=(
                            MediaResponse(media=media_url)
                            if media_url
                            else None
                        ),
                    )
                )

            return user_summaries

        except Exception as e:
            ErrorLogger.log(e)
            return []

    @staticmethod
    def login(email, otp):
        email = (email or "").strip().lower()

        try:
            otp_result = OTPService.verify_otp(email, otp)

            if not otp_result.success:
                return otp_result

            user = frappe.db.get_value("User", {"email": email}, ["name", "first_name"],as_dict=True)
            if not user:
                return Result.not_found(message="User not found.")

            user_name = user.name

            frappe.local.login_manager.user = user_name
            frappe.local.login_manager.post_login()
            profile = frappe.db.get_value(
                "User Profile",
                {"user": user_name},
                [
                    "phone",
                   "country",
                   "geo_l1",
                   "geo_l2"
                ]
            )
            phone = profile[0] if profile else None
            country = profile[1] if profile else None
            geo_l1 = profile[2] if profile else None
            geo_l2 = profile[3] if profile else None
            geo_l1_name = None
            if geo_l1:
               geo_l1_name = frappe.db.get_value(
                   "Geography L1",
                    geo_l1,
                   "geo_l1"
                )
            geo_l2_name = None
            if geo_l2:
               geo_l2_name = frappe.db.get_value(
                   "Geography L2",
                    geo_l2,
                   "geo_l2"
                )    

            return Result.success(
                message="Login successful.",
                data={
                    "user_id": user_name,
                    "full_name": user.first_name,
                    "phone": phone,
                    "location": {
                        "country": country,
                        "geo_l1": geo_l1_name,
                        "geo_l2": geo_l2_name,
                    },
                    "sid": frappe.session.sid,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)

            return Result.failure(
                message="Failed to login.",
                data={"error": str(e)},
                error_data={"traceback": frappe.get_traceback()},
            )