import frappe
from frappe.model.document import Document


class Crisis(Document):

    def on_update(self):
        self.update_opportunity_discovery()

    def update_opportunity_discovery(self):
        for row in self.volunteer_opportunity:
            if not row.child_vol_opportunity:
                continue

            opportunity = frappe.get_doc(
                "Opportunity Discovery",
                row.child_vol_opportunity
            )

            opportunity.crisis_link = self.name
            opportunity.save(ignore_permissions=True)