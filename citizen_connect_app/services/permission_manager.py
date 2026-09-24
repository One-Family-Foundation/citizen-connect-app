import frappe


def ngo_profile_query(user=None):
    if not user:
        user = frappe.session.user

    # Full access
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""

    user = frappe.db.escape(user)

    return f"""
        EXISTS (
            SELECT 1
            FROM `tabUser Child Table` org_user
            WHERE org_user.parent = `tabOrganisation`.name
              AND org_user.parenttype = 'Organisation'
              AND org_user.parentfield = 'ngo_admin'
              AND org_user.user = {user}
             
        )
    """
def case_query(user=None):
    if not user:
        user = frappe.session.user

    # Full access
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""

    user = frappe.db.escape(user)

    return f"""
        (
            -- Service Request:
            -- User must be an NGO Admin of the Organisation linked to the Case
            (
                `tabCase`.type = 'Service Request'
                AND EXISTS (
                    SELECT 1
                    FROM `tabUser Child Table` org_user
                    WHERE org_user.parent = `tabCase`.ngo
                      AND org_user.parenttype = 'Organisation'
                      AND org_user.parentfield = 'ngo_admin'
                      AND org_user.user = {user}
                )
            )

            OR

            -- Other Case types:
            -- Assigned case
            (
                `tabCase`.type != 'Service Request'
                AND `tabCase`.ngo_admin = {user}
            )

            OR

            -- Other Case types:
            -- Unassigned + category-based access
            (
                `tabCase`.type != 'Service Request'
                AND (`tabCase`.ngo_admin IS NULL OR `tabCase`.ngo_admin = '')
                AND EXISTS (
                    SELECT 1
                    FROM `tabOrganisation` org
                    INNER JOIN `tabUser Child Table` org_user
                        ON org_user.parent = org.name
                        AND org_user.parenttype = 'Organisation'
                        AND org_user.parentfield = 'ngo_admin'
                    INNER JOIN `tabCategory Child Table` org_cat
                        ON org_cat.parent = org.name
                        AND org_cat.parenttype = 'Organisation'
                        AND org_cat.parentfield = 'category_l1'
                    WHERE org_user.user = {user}
                      AND org_cat.category = `tabCase`.category
                )
            )
        )
    """
import frappe


def opportunity_form_query(user=None):
    if not user:
        user = frappe.session.user

    # Full access
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""

    user = frappe.db.escape(user)

    return f"""
        EXISTS (
            SELECT 1
            FROM `tabUser Child Table` org_user
            WHERE org_user.parent = `tabOpportunity Form`.ngo
              AND org_user.parenttype = 'Organisation'
              AND org_user.parentfield = 'ngo_admin'
              AND org_user.user = {user}
        )
    """    