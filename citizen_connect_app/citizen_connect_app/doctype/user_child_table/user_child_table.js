function set_ngo_admin_query(frm) {
    const grid = frm.fields_dict.ngo_admin?.grid;

    if (!grid) {
        return;
    }

    const field = grid.get_field("user");

    if (!field) {
        return;
    }

    field.get_query = function () {
        return {
            query: "citizen_connect_app.citizen_connect_app.doctype.ngo_admin.ngo_admin.get_ngo_admin_users"
        };
    };
}