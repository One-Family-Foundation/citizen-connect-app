import frappe
from frappe import _
from citizen_connect_app.models.user import User
from pydantic import ValidationError
from citizen_connect_app.services.otp_service import OTPService
from samaaja.utils.result import Result


class UserManager:
	"""Service layer for registration and OTP-based login.

	OTP issuance/verification is delegated entirely to OTPService —
	this class does not touch the OTP cache directly.
	"""

	@staticmethod
	def register(full_name, email, mobile_no,location):
		email = (email or "").strip().lower()

		if not OTPService.is_verified(email):
			return {"success": False, "message": "Please verify your email with an OTP before registering."}

		try:
			user_data = User(
				full_name=full_name,
				email=email,
			)
		except ValidationError as e:
			return Result.bad_request(message=e.errors()[0]["msg"])

		if frappe.db.exists("User", {"email": user_data.email}):
			return Result.bad_request(message="Email already registered.")


		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": user_data.email,
				"first_name": user_data.full_name,
				"mobile_no": user_data.mobile_no,
				"location":user_data.location,
				"enabled": 1,
				
				"send_welcome_email": 0,
			}
		)
		user.insert(ignore_permissions=True)

		frappe.local.login_manager.user = user.name
		frappe.local.login_manager.post_login()

		OTPService.clear_verified(email)

		return {
			"success": True,
			"user_id": user.name,
			"full_name": user.full_name,
			"email": user.email,
			"mobile_no": user.mobile_no,
			"sid": frappe.session.sid,
		}

	# ------------------------------------------------------------------
	# Login
	# ------------------------------------------------------------------

	@staticmethod
	def login(email, otp):
		email = (email or "").strip().lower()

		if not OTPService.verify_otp(email, otp):
			return {"success": False, "message": "Invalid or expired OTP."}

		user_name = frappe.db.get_value("User", {"email": email}, "name")
		if not user_name:
			frappe.throw(_("User not found."))

		frappe.local.login_manager.user = user_name
		frappe.local.login_manager.post_login()

		return {
			"success": True,
			"user_id": user_name,
			"sid": frappe.session.sid,
		}