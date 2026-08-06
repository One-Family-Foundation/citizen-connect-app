frappe.ui.form.on("Opportunity Discovery", {
    refresh(frm) {

        // Show only L1 categories
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
            return {
                filters: {
                    country_name: frm.doc.country
                }
            };
        });

        // Show only Geography L2 for selected Geography L1
        frm.set_query("geo_l2", function () {
            return {
                filters: {
                    geo_l1: frm.doc.geo_l1
                }
            };
        });
    },

    category_l1(frm) {
        frm.set_value("category_l2", "");
    },

    country(frm) {
        frm.set_value("geo_l1", "");
        frm.set_value("geo_l2", "");
    },

    geo_l1(frm) {
        frm.set_value("geo_l2", "");
    },

    validate(frm) {

        if (frm.doc.title) {
            const len = frm.doc.title.trim().length;

            if (len < 5 || len > 120) {
                frappe.throw(__("Title must be between 5 and 120 characters."));
            }
        }

        if (frm.doc.description) {
            const len = frm.doc.description.trim().length;

            if (len < 20 || len > 400) {
                frappe.throw(__("Description must be between 20 and 400 characters."));
            }
        }

        if (frm.doc.expected_time) {
            const len = frm.doc.expected_time.trim().length;

            if (len < 3 || len > 60) {
                frappe.throw(__("Expected Time must be between 3 and 60 characters."));
            }
        }
    }
});