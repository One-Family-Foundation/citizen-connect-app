// Copyright (c) 2026, One Family Foundation and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Scheme", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Scheme", {
    refresh(frm) {

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

    country(frm) {
        frm.set_value("geo_l1", "");
        frm.set_value("geo_l2", "");
    },

    geo_l1(frm) {
        frm.set_value("geo_l2", "");
    }
});