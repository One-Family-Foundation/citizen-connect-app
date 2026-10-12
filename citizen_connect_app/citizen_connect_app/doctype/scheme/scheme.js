// Copyright (c) 2026, One Family Foundation and contributors
// For license information, please see license.txt
let GEO_L2_PARENT = {};
frappe.ui.form.on("Scheme", {
    before_load(frm) {
        if (frm.is_new()) {
            frm.set_value("country", "");
        }
    },
    refresh(frm) {

        // Show only L1 categories
        frm.set_df_property("rating", "read_only", 1);

        frm.set_query("category_l1", function () {
            return {
                filters: {
                    category_level: "L1"
                }
            };
        });

        // Show only L2 categories under selected L1
        frm.set_query("category_l2", function () {
            if (!frm.doc.category_l1) {
                frappe.msgprint(__("Please select Category L1 first."));
                return {
                    filters: {
                        name: ""
                    }
                };
            }

            return {
                filters: {
                    category_level: "L2",
                    parent_category: frm.doc.category_l1
                }
            };
        });

        // Show only Geography L1 for selected Country
        frm.set_query("geo_l1", function () {
            const country = frm.doc.country;

            return {
                filters: {
                    country_name: country  || "__no_country_selected__"
                }
            };
        });

        // Show only Geography L2 for selected Geography L1
        frm.set_query("geo_l2", () => {
            const geo_l1 = (frm.doc.geo_l1 || [])
                .map(r => r.geo_l1)
                .filter(Boolean);

            return {
                filters: {
                    geo_l1: ["in", geo_l1.length ? geo_l1 : [""]]
                }
            };
        });
    },
    category_l1(frm) {
        frm.set_value("category_l2", "");
    },

    country(frm) {
        frm.clear_table("geo_l1");
        frm.clear_table("geo_l2");
    
        frm.refresh_field("geo_l1");
        frm.refresh_field("geo_l2");
    },

    geo_l1(frm) {
        frm.clear_table("geo_l2");
      frm.refresh_field("geo_l2");
    }
});
function validate_length(value, label, min, max) {
    if (!value) return;

    value = value.trim();

    if (value.length < min) {
        frappe.throw(__("{0} must be at least {1} characters long.", [label, min]));
    }

    if (value.length > max) {
        frappe.throw(__("{0} cannot exceed {1} characters.", [label, max]));
    }
}

frappe.ui.form.on("Scheme", {
    validate(frm) {

        if (frm.doc.application_url) {
            try {
                const url = new URL(frm.doc.application_url);

                if (!["http:", "https:"].includes(url.protocol)) {
                    frappe.throw(__("Application URL must start with http:// or https://"));
                }
            } catch (e) {
                frappe.throw(__("Please enter a valid Application URL."));
            }
        }

        validate_length(frm.doc.scheme_name, "Scheme Name", 5, 120);
        validate_length(frm.doc.description, "Description", 20, 400);
        validate_length(frm.doc.benefit, "Benefits", 20, 1000);
        validate_length(frm.doc.eligibility, "Eligibility", 20, 1000);
        validate_length(frm.doc.documents_required, "Documents Required", 10, 800);
        validate_length(frm.doc.issuing_body, "Issuing Body", 3, 120);
    }
});