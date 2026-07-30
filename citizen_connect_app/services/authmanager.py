import secrets

import frappe
from frappe import _
from frappe.utils import add_to_date, now_datetime, validate_email_address

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5


class UserManager:
	"""Service layer for registration, OTP verification and OTP-based login.

	All persistence goes through the Frappe ORM (frappe.get_doc / get_value /
	exists / delete_doc) — no raw SQL is used anywhere in this file.
	"""

	# ------------------------------------------------------------------
	# Helpers
	# ------------------------------------------------------------------

	

	@staticmethod
	def _generate_otp():
		return str(secrets.randbelow(900000) + 100000)

	@staticmethod
	def _dispatch_otp(email, otp, purpose):
		"""Placeholder for SMTP/SMS delivery. Until credentials are
		configured, the OTP is printed to the console (bench/worker logs)."""
		banner = "=" * 60
		print(f"\n{banner}\n[DEV OTP] {purpose} OTP for {email}: {otp}\n"
			f"(valid for {OTP_EXPIRY_MINUTES} minutes)\n{banner}\n")
		frappe.logger().info(f"[DEV OTP] {purpose} OTP for {email}: {otp}")

	@staticmethod
	def _create_otp_record(email, purpose):
		# Invalidate any previous unused OTPs for this email + purpose
		existing = frappe.get_all(
			"OTP",
			filters={"email": email, "purpose": purpose, "is_used": 0},
			pluck="name",
		)
		for name in existing:
			frappe.delete_doc("OTP", name, ignore_permissions=True, force=True)

		otp = UserManager._generate_otp()

		otp_doc = frappe.get_doc(
			{
				"doctype": "OTP",
				"email": email,
				"purpose": purpose,
				"otp": otp,
				"expires_at": add_to_date(now_datetime(), minutes=OTP_EXPIRY_MINUTES),
				"attempts": 0,
				"is_used": 0,
			}
		)
		otp_doc.insert(ignore_permissions=True)

		return otp

	@staticmethod
	def _verify_otp_record(email, purpose, otp):
		"""Raises frappe.ValidationError (via frappe.throw) if invalid/expired."""
		otp_name = frappe.get_value(
			"OTP",
			{"email": email, "purpose": purpose, "is_used": 0},
			"name",
			order_by="creation desc",
		)

		if not otp_name:
			frappe.throw(_("No OTP request found. Please request a new OTP."))

		otp_doc = frappe.get_doc("OTP", otp_name)

		if now_datetime() > otp_doc.expires_at:
			frappe.delete_doc("OTP", otp_name, ignore_permissions=True, force=True)
			frappe.throw(_("OTP has expired. Please request a new one."))

		if otp_doc.attempts >= OTP_MAX_ATTEMPTS:
			frappe.delete_doc("OTP", otp_name, ignore_permissions=True, force=True)
			frappe.throw(_("Too many incorrect attempts. Please request a new OTP."))

		if otp_doc.otp != str(otp or "").strip():
			otp_doc.attempts += 1
			otp_doc.save(ignore_permissions=True)
			frappe.throw(_("Invalid OTP."))

		otp_doc.is_used = 1
		otp_doc.save(ignore_permissions=True)

	# ------------------------------------------------------------------
	# Registration
	# ------------------------------------------------------------------

	@staticmethod
	def register(full_name, email, mobile_no):
		full_name = (full_name or "").strip()
		email = (email or "").strip().lower()
		mobile_no = (mobile_no or "").strip()

		if not full_name:
			frappe.throw(_("Full Name is required."))
		if not email:
			frappe.throw(_("Email is required."))
		if not mobile_no:
			frappe.throw(_("Mobile Number is required."))

		if len(full_name) < 3 or len(full_name) > 120:
			frappe.throw(_("Full Name must be between 3 and 120 characters."))
		if len(email) < 5 or len(email) > 254:
			frappe.throw(_("Invalid Email Address."))
		if len(mobile_no) < 6 or len(mobile_no) > 15:
			frappe.throw(_("Mobile Number must be between 6 and 15 digits."))
		if not mobile_no.isdigit():
			frappe.throw(_("Mobile Number must contain only digits."))

		validate_email_address(email, throw=True)

		if frappe.db.exists("User", {"email": email}):
			frappe.throw(_("Email already registered."))
		if frappe.db.exists("User", {"mobile_no": mobile_no}):
			frappe.throw(_("Mobile Number already registered."))

		
		# Account is created disabled and only enabled once the
		# registration OTP is verified.
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": full_name,
				"mobile_no": mobile_no,
				"enabled": 0,
				"send_welcome_email": 0,
			}
		)
		user.insert(ignore_permissions=True)

		otp = UserManager._create_otp_record(email, purpose="Registration")
		UserManager._dispatch_otp(email, otp, purpose="Registration")

		return {
			"user_id": user.name,
			"full_name": user.full_name,
			"email": user.email,
			"mobile_no": user.mobile_no,
			"otp_expires_in_minutes": OTP_EXPIRY_MINUTES,
		}

	@staticmethod
	def verify_registration_otp(email, otp):
		email = (email or "").strip().lower()
		if not email or not otp:
			frappe.throw(_("Email and OTP are required."))

		if not frappe.db.exists("User", {"email": email}):
			frappe.throw(_("User not found."))

		UserManager._verify_otp_record(email, purpose="Registration", otp=otp)

		user = frappe.get_doc("User", email)
		user.enabled = 1
		user.save(ignore_permissions=True)

		return {
			"user_id": user.name,
			"full_name": user.full_name,
			"email": user.email,
			"verified": True,
		}

	@staticmethod
	def resend_otp(email, purpose="Registration"):
		email = (email or "").strip().lower()
		if not email:
			frappe.throw(_("Email is required."))

		if not frappe.db.exists("User", {"email": email}):
			frappe.throw(_("User not found."))

		if purpose == "Registration" and frappe.db.get_value("User", email, "enabled"):
			frappe.throw(_("User already verified."))

		otp = UserManager._create_otp_record(email, purpose=purpose)
		UserManager._dispatch_otp(email, otp, purpose=purpose)

		return {"email": email, "otp_expires_in_minutes": OTP_EXPIRY_MINUTES}

	# ------------------------------------------------------------------
	# Login (OTP based — no password prompt)
	# ------------------------------------------------------------------

	@staticmethod
	def login_request_otp(email):
		email = (email or "").strip().lower()
		if not email:
			frappe.throw(_("Email is required."))

		user_name = frappe.db.get_value("User", {"email": email}, "name")
		if not user_name:
			frappe.throw(_("User not found."))

		if not frappe.db.get_value("User", user_name, "enabled"):
			frappe.throw(_("Account not verified. Please complete registration first."))

		otp = UserManager._create_otp_record(email, purpose="Login")
		UserManager._dispatch_otp(email, otp, purpose="Login")

		return {"email": email, "otp_expires_in_minutes": OTP_EXPIRY_MINUTES}

	@staticmethod
	def login_verify_otp(email, otp):
		email = (email or "").strip().lower()
		if not email or not otp:
			frappe.throw(_("Email and OTP are required."))

		user_name = frappe.db.get_value("User", {"email": email}, "name")
		if not user_name:
			frappe.throw(_("User not found."))

		UserManager._verify_otp_record(email, purpose="Login", otp=otp)

		frappe.local.login_manager.user = user_name
		frappe.local.login_manager.post_login()

		user = frappe.get_doc("User", user_name)

		return {
			"user_id": user.name,
			"full_name": user.full_name,
			"email": user.email,
			"mobile_no": user.mobile_no,
			"sid": frappe.session.sid,
		}