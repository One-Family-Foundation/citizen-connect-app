# Copyright (c) 2026, One Family Foundation and contributors

# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OpportunityDiscovery(Document):

    def on_update(self):
        old_doc = self.get_doc_before_save()

        # Crisis link changed
        if old_doc and old_doc.crisis_link != self.crisis_link:

            # Remove from old crisis
            if old_doc.crisis_link:
                self._remove_from_crisis(old_doc.crisis_link)

            # Add to new crisis
            if self.crisis_link:
                self._add_to_crisis(self.crisis_link)

        # New opportunity with crisis
        elif not old_doc and self.crisis_link:
            self._add_to_crisis(self.crisis_link)

    def _add_to_crisis(self, crisis_name):
        crisis = frappe.get_doc("Crisis", crisis_name)

        for row in crisis.volunteer_opportunity:
            if row.child_vol_opportunity == self.name:
                row.num_of_volunteer = self.number_of_volunteer
                crisis.save(ignore_permissions=True)
                return

        crisis.append("volunteer_opportunity", {
            "child_vol_opportunity": self.name,
            "num_of_volunteer": self.number_of_volunteer,
        })

        crisis.save(ignore_permissions=True)

    def _remove_from_crisis(self, crisis_name):
        crisis = frappe.get_doc("Crisis", crisis_name)

        crisis.volunteer_opportunity = [
            row
            for row in crisis.volunteer_opportunity
            if row.child_vol_opportunity != self.name
        ]

        crisis.save(ignore_permissions=True)