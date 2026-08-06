import secrets
import frappe
from frappe import _
from frappe.utils import validate_email_address
from samaaja.utils.result import Result
OTP_EXPIRY_MINUTES = 5
VERIFIED_EXPIRY_MINUTES = 15


class OTPService:

	@staticmethod
	def _cache_key(email):
		return f"otp:{email.lower()}"

	@staticmethod
	def _verified_cache_key(email):
		return f"otp-verified:{email.lower()}"

	@staticmethod
	def _generate_otp():
		# 4-digit OTP: 1000-9999
		return "1234"
		#return str(secrets.randbelow(9000) + 1000)

	@staticmethod
	def send_otp(email):
		email = (email or "").strip().lower()
		if not email:
			return Result.bad_request(
             message="Email is required."
            )

		validate_email_address(email, throw=True)

		otp = OTPService._generate_otp()

		frappe.cache().set_value(
			OTPService._cache_key(email),
			otp,
			expires_in_sec=OTP_EXPIRY_MINUTES * 60,
		)

		return Result.success(
               message="OTP sent successfully.",
             data={
                "email": email,
                "otp": otp,
                "otp_expires_in_minutes": OTP_EXPIRY_MINUTES,
            },
        )

	@staticmethod
	def verify_otp(email, otp):
		email = (email or "").strip().lower()
		if not email or not otp:
			return Result.bad_request(
                   message="Email and OTP are required."
            )

		key = OTPService._cache_key(email)
		cached_otp = frappe.cache().get_value(key)

		if not cached_otp:
			return Result.bad_request(
                 message="OTP has expired."
            )

		if str(cached_otp) != str(otp).strip():
			return Result.bad_request(
                message="Invalid OTP."
            )

		frappe.cache().delete_value(key)

		frappe.cache().set_value(
			OTPService._verified_cache_key(email),
			True,
			expires_in_sec=VERIFIED_EXPIRY_MINUTES * 60,
		)

		return Result.success(
               message="OTP verified successfully.",
               data={
                  "verified": True,
                },
        )

	@staticmethod
	def is_verified(email):
		email = (email or "").strip().lower()
		return bool(frappe.cache().get_value(OTPService._verified_cache_key(email)))

	@staticmethod
	def clear_verified(email):
		email = (email or "").strip().lower()
		frappe.cache().delete_value(OTPService._verified_cache_key(email))