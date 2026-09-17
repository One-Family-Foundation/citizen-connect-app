
frappe.ui.form.on("Service", {
    refresh(frm) {
        frm.set_df_property("rating", "read_only", 1);

        toggle_sponsorship_information(frm)

        // Category L1
        frm.set_query("category_l1", function () {
            return {
                filters: {
                    category_level: "L1"
                }
            };
        });

        // Category L2
        frm.set_query("category_l2", function () {
            if (!frm.doc.category_l1) {
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

        // Geography L1
        frm.set_query("service_geo1", function () {
            if (!frm.doc.service_country) {
                return {
                    filters: {
                        name: ""
                    }
                };
            }

            return {
                filters: {
                    country_name: frm.doc.service_country
                }
            };
        });

        // Geography L2
        frm.set_query("service_geo2", function () {
            if (!frm.doc.service_geo1) {
                return {
                    filters: {
                        name: ""
                    }
                };
            }

            return {
                filters: {
                    geo_l1: frm.doc.service_geo1
                }
            };
        });
    },
    cost_model(frm) {
        toggle_sponsorship_information(frm);
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
    },

    validate(frm) {
        // --------------------------------
        // FIELD LENGTH LIMITS
        // --------------------------------

        const limits = {
            title: {min:5,max:120},
            description: {min:20,max:400},
            sponsorship_information: {min:20,max:400},
            eligibility_condition: {min:20 , max:400}
        };

        for (const [fieldname, maxLength] of Object.entries(limits)) {
            const value = frm.doc[fieldname];

            if (!value) {
                continue;
            }

            if (value.length > maxLength) {
                frappe.msgprint({
                    title: __("Invalid Input"),
                    message: __(
                        "{0} cannot be more than {1} characters.",
                        [
                            frm.fields_dict[fieldname].df.label,
                            maxLength
                        ]
                    ),
                    indicator: "red"
                });

                frappe.validated = false;
                return;
            }
        }

        // --------------------------------
        // BLOCK HTML TAGS
        // --------------------------------

        const textFields = [
            "title",
            "description",
            "sponsorship_information",
            "eligibility_condition"
        ];

        const htmlPattern = /<\s*\/?\s*[a-z][^>]*>/i;

        for (const fieldname of textFields) {
            const value = frm.doc[fieldname];

            if (!value) {
                continue;
            }

            if (htmlPattern.test(value)) {
                frappe.msgprint({
                    title: __("Invalid Input"),
                    message: __(
                        "HTML tags are not allowed in {0}.",
                        [frm.fields_dict[fieldname].df.label]
                    ),
                    indicator: "red"
                });

                frappe.validated = false;
                return;
            }
        }

        // --------------------------------
        // BLOCK JAVASCRIPT / DANGEROUS URL
        // --------------------------------

        const dangerousPattern =
            /javascript\s*:|vbscript\s*:|data\s*:\s*text\/html|on\w+\s*=/i;

        for (const fieldname of textFields) {
            const value = frm.doc[fieldname];

            if (!value) {
                continue;
            }

            if (dangerousPattern.test(value)) {
                frappe.msgprint({
                    title: __("Invalid Input"),
                    message: __(
                        "Unsafe content is not allowed in {0}.",
                        [frm.fields_dict[fieldname].df.label]
                    ),
                    indicator: "red"
                });

                frappe.validated = false;
                return;
            }
        }

        // --------------------------------
        // EMAIL VALIDATION
        // --------------------------------

        if (frm.doc.email) {
            const emailPattern =
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailPattern.test(frm.doc.email)) {
                frappe.msgprint({
                    title: __("Invalid Email"),
                    message: __("Please enter a valid email address."),
                    indicator: "red"
                });

                frappe.validated = false;
                return;
            }
        }

        // --------------------------------
        // COST VALIDATION
        // --------------------------------

        if (frm.doc.cost_model === "Free" && frm.doc.cost_details) {
            frappe.msgprint({
                title: __("Invalid Cost"),
                message: __("Cost should be empty when Cost Model is Free."),
                indicator: "red"
            });

            frappe.validated = false;
            return;
        }

        if (
            frm.doc.cost_model === "Paid" &&
            frm.doc.cost_details != null &&
            frm.doc.cost_details < 0
        ) {
            frappe.msgprint({
                title: __("Invalid Cost"),
                message: __("Cost cannot be negative."),
                indicator: "red"
            });

            frappe.validated = false;
            return;
        }
    }
});
function toggle_sponsorship_information(frm) {
    const is_paid = frm.doc.cost_model === "Paid";

    frm.toggle_display("sponsorship_information", is_paid);
    frm.toggle_display("cost_details", is_paid);

    if (!is_paid) {
        frm.set_value("sponsorship_information", "");
        frm.set_value("cost_details", "");
    }
}