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

@frappe.whitelist()
def delete_scheme(scheme_name):
    cases = frappe.get_all(
        "Case",
        filters={"scheme_id": scheme_name},
        pluck="name"
    )
    for case_name in cases:
        frappe.delete_doc(
            "Case",
            case_name,
            ignore_permissions=True
        )
    frappe.delete_doc(
        "Scheme",
        scheme_name,
        ignore_permissions=True
    )
    frappe.db.commit()
    return {
        "success": True,
        "message": "Scheme and all linked Cases deleted successfully"
    }