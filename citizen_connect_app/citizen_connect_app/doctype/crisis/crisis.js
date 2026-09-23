
frappe.ui.form.on("Crisis", {
    refresh(frm) {
        // Show only Geography L1 for selected Country
        frm.set_query("geo_l1", function () {
            if (!frm.doc.country) {
                return {
                    filters: {
                        name: ""
                    }
                };
            }

            return {
                filters: {
                    country_name: frm.doc.country
                }
            };
        });

        // Show only Category L1
        frm.set_query("category", function () {
            return {
                filters: {
                    category_level: "L1"
                }
            };
        });

        // Show only Geography L2 for selected Geography L1
        frm.set_query("geo_l2", function () {
            if (!frm.doc.geo_l1) {
                return {
                    filters: {
                        name: ""
                    }
                };
            }

            return {
                filters: {
                    geo_l1: frm.doc.geo_l1
                }
            };
        });

        // Show/hide Crisis Summary based on status
        toggle_crisis_summary(frm);
    },

    // When Country changes, clear dependent fields
    country(frm) {
        frm.set_value("geo_l1", "");
        frm.set_value("geo_l2", "");
    },

    // When Geo L1 changes, clear Geo L2
    geo_l1(frm) {
        frm.set_value("geo_l2", "");
    },

    // When Status changes
    status(frm) {
        toggle_crisis_summary(frm);
    },

    validate(frm) {
        // Validate Title
        if (frm.doc.title) {
            const len = frm.doc.title.trim().length;

            if (len < 5 || len > 120) {
                frappe.throw(
                    __("Title must be between 5 and 120 characters.")
                );
            }
        }

        // Validate Description
        if (frm.doc.description) {
            const len = frm.doc.description.trim().length;

            if (len < 20 || len > 600) {
                frappe.throw(
                    __("Description must be between 20 and 600 characters.")
                );
            }
        }

        // Validate Crisis Summary
        if (frm.doc.crisis_summary) {
            const len = frm.doc.crisis_summary.trim().length;

            if (len < 20 || len > 600) {
                frappe.throw(
                    __("Crisis Summary must be between 20 and 600 characters.")
                );
            }
        }

        if (frm.doc.location_address) {
            const len = frm.doc.location_address.trim().length;

            if (len < 20 || len > 200) {
                frappe.throw(
                    __("Location address must be between 20 and 200 characters.")
                );
            }
        }

        if (frm.doc.location_name) {
            const len = frm.doc.location_name.trim().length;

            if (len < 20 || len > 200) {
                frappe.throw(
                    __("Location name must be between 20 and 200 characters.")
                );
            }
        }

        if (frm.doc.verification_status) {
            const len = frm.doc.verification_status.trim().length;

            if (len < 20 || len > 300) {
                frappe.throw(
                    __("Verification status must be between 20 and 300 characters.")
                );
            }
        }
    }
});


// Show Crisis Summary only for Inactive crisis
function toggle_crisis_summary(frm) {
    const is_inactive = frm.doc.status === "Inactive";

    frm.set_df_property(
        "crisis_summary",
        "hidden",
        !is_inactive
    );

    // Make Crisis Summary mandatory only for Inactive crisis
    frm.set_df_property(
        "crisis_summary",
        "reqd",
        is_inactive
    );

    // Clear summary when crisis becomes Active
    if (!is_inactive && frm.doc.crisis_summary) {
        frm.set_value("crisis_summary", "");
    }
}

