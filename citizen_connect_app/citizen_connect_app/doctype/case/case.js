frappe.ui.form.on("Case", {
    refresh(frm) {
        update_case_summary(frm);
        update_complete_button(frm);
    },

    workflow_state(frm) {
        update_case_summary(frm);
        update_complete_button(frm);
    },

    case_summary(frm) {
        update_complete_button(frm);
    }
});

function update_case_summary(frm) {
    const state = frm.doc.workflow_state;

    const is_in_progress = state === "In Progress";
    const is_resolved = state === "Resolved";
    const is_closed = state === "Closed";

    frm.set_df_property(
        "case_summary",
        "hidden",
        !is_in_progress && !is_resolved && !is_closed
    );

    frm.set_df_property(
        "case_summary",
        "read_only",
        !is_in_progress
    );
}

function update_complete_button(frm) {
    if (frm.doc.workflow_state !== "In Progress") {
        return;
    }

    const has_summary = Boolean(
        frm.doc.case_summary &&
        frm.doc.case_summary.trim().length > 0
    );

    const disable_complete_button = () => {
        frm.page.wrapper.find("button").each(function () {
            const button = $(this);

            if (button.text().trim() === "Complete") {
                button.prop("disabled", !has_summary);

                if (!has_summary) {
                    button.attr(
                        "title",
                        "Please enter Case Summary before completing the Case."
                    );
                } else {
                    button.removeAttr("title");
                }
            }
        });
    };

    disable_complete_button();

    setTimeout(disable_complete_button, 100);
    setTimeout(disable_complete_button, 500);
    setTimeout(disable_complete_button, 1000);
}