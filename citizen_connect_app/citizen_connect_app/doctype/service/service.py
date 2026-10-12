# Copyright (c) 2026, One Family Foundation and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Service(Document):
    def validate(self):
        if self.is_new():
            if not self.service_status:
                self.service_status = "Pending"
            return

        user = frappe.get_doc("User", frappe.session.user)

        if user.role_profile_name == "NGO Admin Role Profile" and self.service_status == "Approved":
            self.service_status = "Pending"


@frappe.whitelist()
def delete_service(service_name):
    cases = frappe.get_all(
        "Case",
        filters={"service_id": service_name},
        pluck="name"
    )

    # Delete all Cases linked to this Service
    for case_name in cases:
        frappe.delete_doc(
            "Case",
            case_name,
            ignore_permissions=True
        )

    # Now delete the Service
    frappe.delete_doc(
        "Service",
        service_name,
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True,
        "message": "Service and all linked Cases deleted successfully"
    }