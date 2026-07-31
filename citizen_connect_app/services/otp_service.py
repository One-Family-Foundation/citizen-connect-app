import secrets
import frappe
from frappe import _
from frappe.utils import validate_email_address

OTP_EXPIRY_MINUTES = 5
VERIFIED_EXPIRY_MINUTES = 15


class OTPService:
	"""Generic OTP issuance/verification, keyed only by email.

	Verifying an OTP does not immediately log anyone in or register
	them — it sets a separate "verified" flag in cache for this email,
	valid for VERIFIED_EXPIRY_MINUTES. Register checks that flag rather
	than re-running OTP verification itself, so the OTP is consumed
	exactly once, at verify time.
	"""

	@staticmethod
	def _cache_key(email):
		return f"otp:{email.lower()}"

	@staticmethod
	def _verified_cache_key(email):
		return f"otp-verified:{email.lower()}"

	@staticmethod
	def _generate_otp():
		# 4-digit OTP: 1000-9999
		return str(secrets.randbelow(9000) + 1000)

	@staticmethod
	def send_otp(email):
		email = (email or "").strip().lower()
		if not email:
			frappe.throw(_("Email is required."))

		validate_email_address(email, throw=True)

		otp = OTPService._generate_otp()

		frappe.cache().set_value(
			OTPService._cache_key(email),
			otp,
			expires_in_sec=OTP_EXPIRY_MINUTES * 60,
		)

		# FOR NOW: return the OTP directly since no email/SMS delivery
		# channel is wired up yet. This must be removed/gated behind a
		# dev-only flag before this goes anywhere near production —
		# see the note in the response from earlier in this thread.
		return {
			"email": email,
			"otp": otp,
			"otp_expires_in_minutes": OTP_EXPIRY_MINUTES,
		}

	@staticmethod
	def verify_otp(email, otp):
		email = (email or "").strip().lower()
		if not email or not otp:
			frappe.throw(_("Email and OTP are required."))

		key = OTPService._cache_key(email)
		cached_otp = frappe.cache().get_value(key)

		if not cached_otp:
			return False

		if str(cached_otp) != str(otp).strip():
			return False

		frappe.cache().delete_value(key)

		# Mark this email as verified so register() can check it later
		# without needing the OTP again.
		frappe.cache().set_value(
			OTPService._verified_cache_key(email),
			True,
			expires_in_sec=VERIFIED_EXPIRY_MINUTES * 60,
		)

		return True

	@staticmethod
	def is_verified(email):
		email = (email or "").strip().lower()
		return bool(frappe.cache().get_value(OTPService._verified_cache_key(email)))

	@staticmethod
	def clear_verified(email):
		email = (email or "").strip().lower()
		frappe.cache().delete_value(OTPService._verified_cache_key(email))