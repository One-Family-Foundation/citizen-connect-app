frappe.ui.form.on("Service", {
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
        frm.set_query("service_geo1", function () {
            return {
                filters: {
                    country_name: frm.doc.service_country
                }
            };
        });

        // Show only Geography L2 for selected Geography L1
        frm.set_query("service_geo2", function () {
            return {
                filters: {
                    geo_l1: frm.doc.service_geo1
                }
            };
        });
    },

    category_l1(frm) {
        frm.set_value("category_l2", "");
    },

    service_country(frm) {
        frm.set_value("service_geo1", "");
        frm.set_value("service_geo2", "");
    },

    service_geo1(frm) {
        frm.set_value("service_geo2", "");
    }
});