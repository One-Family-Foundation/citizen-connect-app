# Copyright (c) 2026, One Family Foundation and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Scheme(Document):
    def validate(self):
        if self.is_new():
            if not self.status:
                self.status = "Pending"
            return

        user = frappe.get_doc("User", frappe.session.user)
        if user.role_profile_name == "NGO Admin Role Profile" and self.status == "Approved":
            self.status = "Pending"