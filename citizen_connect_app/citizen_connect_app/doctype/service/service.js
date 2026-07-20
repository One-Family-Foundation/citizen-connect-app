// Copyright (c) 2026, One Family Foundation and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Service", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Service", {
    refresh(frm) {

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

    service_country(frm) {
        frm.set_value("service_geo1", "");
        frm.set_value("service_geo2", "");
    },

    service_geo1(frm) {
        frm.set_value("service_geo2", "");
    }
});