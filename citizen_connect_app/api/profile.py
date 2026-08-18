import frappe

from samaaja.utils.custom_response import custom_response
from citizen_connect_app.services.profile_manager import (
    update_profile
)


@frappe.whitelist()
def update(
    profile_photo=None,
    alternative_email=None,
    phone=None,
    user_type=None,
    country=None,
    geo_l1=None,
    geo_l2=None,
    org_name=None,
):
    data = {
        "profile_photo": profile_photo,
        "alternative_email": alternative_email,
        "phone": phone,
        "user_type": user_type,
        "org_name": org_name,
    }

    if country is not None or geo_l1 is not None or geo_l2 is not None:
        data["location"] = {
            "country": country,
            "geo1": geo_l1,
            "geo2": geo_l2,
        }

    data = {
        key: value
        for key, value in data.items()
        if value is not None
    }

    return update_profile(data).to_custom_response()