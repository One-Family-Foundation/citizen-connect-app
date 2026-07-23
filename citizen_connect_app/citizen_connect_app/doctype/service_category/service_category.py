import frappe
from frappe import _
from frappe.model.document import Document


class ServiceCategory(Document):

    def validate(self):
        self.validate_category_level()
        self.validate_duplicate_category()

    def validate_category_level(self):
        """Validate category hierarchy."""

        if self.category_level not in ["L1", "L2"]:
            frappe.throw(_("Only L1 and L2 categories are allowed."))

        if self.category_level == "L1":
            if self.parent_service_category:
                frappe.throw(_("L1 categories cannot have a parent."))

        elif self.category_level == "L2":
            if not self.parent_service_category:
                frappe.throw(_("L2 categories must have an L1 parent."))

            parent = frappe.get_doc(
                "Service Category",
                self.parent_service_category,
            )

            if parent.category_level != "L1":
                frappe.throw(
                    _("Parent of an L2 category must be an L1 category.")
                )

    def validate_duplicate_category(self):
        """Prevent duplicate categories under the same parent."""

        duplicate = frappe.db.exists(
            "Service Category",
            {
                "catalogue_name": self.catalogue_name,
                "parent_service_category": self.parent_service_category,
                "name": ["!=", self.name],
            },
        )

        if duplicate:
            if self.parent_service_category:
                frappe.throw(
                    _(
                        "Category '{0}' already exists under the selected parent."
                    ).format(self.catalogue_name)
                )
            else:
                frappe.throw(
                    _(
                        "An L1 category named '{0}' already exists."
                    ).format(self.catalogue_name)
                )