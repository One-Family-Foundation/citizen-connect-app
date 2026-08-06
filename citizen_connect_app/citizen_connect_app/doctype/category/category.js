frappe.ui.form.on("Category", {
    refresh(frm) {
        set_parent_query(frm);
        toggle_fields(frm);
    },

    category_level(frm) {
        toggle_fields(frm);
    }
});

function set_parent_query(frm) {
    frm.set_query("parent_category", function () {
        return {
            filters: {
                category_level: "L1"
            }
        };
    });
}

function toggle_fields(frm) {
    const is_l2 = frm.doc.category_level === "L2";

    // Parent Category mandatory only for L2
    frm.toggle_reqd("parent_category", is_l2);

    // Disable Is Group for L2
    frm.set_df_property("is_group", "read_only", is_l2);

    if (is_l2) {
        // L2 cannot be a group
        frm.set_value("is_group", 0);
    } else {
        // L1 should not have a parent
        frm.set_value("parent_category", "");
    }
}