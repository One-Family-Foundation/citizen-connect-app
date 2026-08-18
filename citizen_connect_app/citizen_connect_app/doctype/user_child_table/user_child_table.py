import frappe
from frappe.model.document import Document


class UserChildTable(Document):
    pass


@frappe.whitelist()
def get_user_child_table_users(
    doctype,
    txt,
    searchfield,
    start,
    page_len,
    filters=None,
):
    start = int(start or 0)
    page_len = int(page_len or 10)

    return frappe.db.sql(
    f"""
        SELECT
            u.name,
            u.full_name
        FROM `tabUser` u
        WHERE u.role_profile_name = 'NGO Admin Role Profile'
          AND u.enabled = 1
          AND (
              u.name LIKE %(txt)s
              OR u.full_name LIKE %(txt)s
          )
        ORDER BY u.full_name
        LIMIT {page_len} OFFSET {start}
        """,
        {
            "txt": f"%{txt or ''}%",
        },
    )