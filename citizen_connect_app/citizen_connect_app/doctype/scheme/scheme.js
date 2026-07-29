// Copyright (c) 2026, One Family Foundation and contributors
// For license information, please see license.txt

frappe.ui.form.on("Scheme", {
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
                    parent_service_category: frm.doc.category_l1
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
    }
});