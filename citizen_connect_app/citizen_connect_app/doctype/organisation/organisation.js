let L2_PARENT = {};
let GEO_L2_PARENT = {};

async function load_l2_map() {
    const rows = await frappe.db.get_list("Category", {
        filters: { category_level: "L2" },
        fields: ["name", "parent_category"],
        limit: 0
    });

    L2_PARENT = Object.fromEntries(
        rows.map(r => [r.name, r.parent_category])
    );
}

async function load_geo_l2_map() {
    const rows = await frappe.db.get_list("Geography L2", {
        fields: ["name", "geo_l1"],
        limit: 0
    });

    GEO_L2_PARENT = Object.fromEntries(
        rows.map(r => [r.name, r.geo_l1])
    );
}

frappe.ui.form.on("Organisation", {
  before_load(frm) {
    if (frm.is_new()) {
        frm.set_value("country", "");
    }
},
  country(frm) {
    frm.clear_table("geo_l1");
    frm.clear_table("geo_l2");
  
    frm.refresh_field("geo_l1");
    frm.refresh_field("geo_l2");
},
    onload: async function (frm) {
        await Promise.all([
            load_l2_map(),
            load_geo_l2_map()
        ]);
    },

    refresh: async function (frm) {
        await Promise.all([
            load_l2_map(),
            load_geo_l2_map()
        ]);
    },

    setup(frm) {
        // Category L1
        frm.set_query("category_l1", () => ({
            filters: { category_level: "L1" }
        }));

        // Category L2
        frm.set_query("category_l2", () => {
            const l1 = (frm.doc.category_l1 || [])
                .map(r => r.category)
                .filter(Boolean);

            return {
                filters: {
                    category_level: "L2",
                    parent_category: ["in", l1.length ? l1 : [""]]
                }
            };
        });

        // Geo L1
       

frm.set_query("geo_l1", () => {
  
    return {
        filters: {
            country_name: frm.doc.country
        }
    };
});


        // Geo L2
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

        // NGO Admin
        frm.set_query("user", "ngo_admin", () => ({
            filters: {
                role_profile_name: "NGO Admin Role Profile",
                enabled: 1
            }
        }));
    },

    category_l1(frm) {
        sync_l2(frm);
    },

    geo_l1(frm) {
        sync_geo_l2(frm);
    },

    validate(frm) {
        sync_l2(frm, true);
        sync_geo_l2(frm, true);
    }
});

frappe.ui.form.on("Category Child Table", {
    category_remove(frm) {
        sync_l2(frm);
    }
});

frappe.ui.form.on("Child Geo L1", {
    geo_l1_remove(frm) {
        sync_geo_l2(frm);
    }
});

function sync_l2(frm, silent = false) {
    const rows = frm.doc.category_l2 || [];

    if (!rows.length) return;

    const l1 = new Set(
        (frm.doc.category_l1 || [])
            .map(r => r.category)
            .filter(Boolean)
    );

    const keep = rows.filter(r => {
        const parent = L2_PARENT[r.category];
        return parent === undefined || l1.has(parent);
    });

    if (keep.length === rows.length) return;

    frm.clear_table("category_l2");

    keep.forEach(r => {
        Object.assign(frm.add_child("category_l2"), {
            category: r.category
        });
    });

    frm.refresh_field("category_l2");

    if (!silent) {
        frappe.show_alert({
            message: __(
                "Removed L2 categories whose parent was deselected"
            ),
            indicator: "orange"
        });
    }
}

function sync_geo_l2(frm, silent = false) {
    const rows = frm.doc.geo_l2 || [];

    if (!rows.length) return;

    const geo_l1 = new Set(
        (frm.doc.geo_l1 || [])
            .map(r => r.geo_l1)
            .filter(Boolean)
    );

    const keep = rows.filter(r => {
        const parent = GEO_L2_PARENT[r.geo_l2];
        return parent === undefined || geo_l1.has(parent);
    });

    if (keep.length === rows.length) return;

    frm.clear_table("geo_l2");

    keep.forEach(r => {
        Object.assign(frm.add_child("geo_l2"), {
            geo_l2: r.geo_l2
        });
    });

    frm.refresh_field("geo_l2");

    if (!silent) {
        frappe.show_alert({
            message: __(
                "Removed Geo L2 locations whose parent was deselected"
            ),
            indicator: "orange"
        });
    }
}

