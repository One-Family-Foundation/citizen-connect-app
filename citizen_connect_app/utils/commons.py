
import frappe
from samaaja.utils.result import Result
from citizen_connect_app.models.utils import Location
from urllib.parse import quote

def create_media_url(media_url: str) -> str|None:
    media_base_url = frappe.utils.get_url().rstrip("/")
    if not media_url:
        return None
    if not media_url.startswith(("http://", "https://")):
       media_url = f"{media_base_url}/{quote(media_url.lstrip('/'), safe='/')}"

    return media_url

def localized(name: str | None, lang: str | None):
    if not name:
        return None

    return {
        "name": name,
        "display_name": frappe._(name, lang=lang),
    }
    
def resolve_location(location:Location)->Result:
    country = None
    geo_l1 = None
    geo_l2 = None
    
    if location.country:
        country = frappe.db.get_value(
            "Country",
            {"country_name": location.country},
            "name"
        )
        if not country:
            return Result.bad_request(
                message="Invalid country selected."
        )
        if location.geo1:
            geo_l1 = frappe.db.get_value(
                "Geography L1",
                {"geo_l1": location.geo1},
                "name"
            )
            if not geo_l1:
                return Result.bad_request(
                message="Invalid Geography L1 selected."
            )
            if location.geo2:
                geo_l2 = frappe.db.get_value(
                    "Geography L2",
                    {"geo_l2": location.geo2},
                    "name"
                )
            if not geo_l2:
                return Result.bad_request(
                    message="Invalid Geography L2 selected."
                )
    return Result.success(message="Location resolved successfully.", data=Location(country=country, geo1=geo_l1, geo2=geo_l2),)

def update_user_category_statistics(user_id, category , is_deleted=False):
    if not user_id or not category:
        return

    stats_name = frappe.db.get_value(
        "User Category Statistics",
        {
            "user": user_id,
            "category_l1": category,
        },
        "name",
    )

    if stats_name:
        stats = frappe.get_doc(
            "User Category Statistics",
            stats_name,
        )

        if is_deleted:
            stats.count = max((stats.count or 0) - 1, 0)
            if stats.count <= 0:
                frappe.delete_doc(
                    "User Category Statistics",
                    stats.name,
                    ignore_permissions=True,
                )
                return
        else:
           stats.count = (stats.count or 0) + 1
        stats.save(ignore_permissions=True)

    elif not is_deleted:
        frappe.get_doc({
            "doctype": "User Category Statistics",
            "user": user_id,
            "category_l1": category,
            "count": 1,
        }).insert(ignore_permissions=True)    