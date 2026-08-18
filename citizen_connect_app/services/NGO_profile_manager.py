import frappe

from citizen_connect_app.models.ngo import Organisation
from citizen_connect_app.utils.error_logger import ErrorLogger

from samaaja.utils.result import Result


def get_profile(organisation: str) -> Result:
    try:
        if not organisation:
            return Result.bad_request(
                message="Organisation is required."
            )

       
        organisation_data = frappe.db.get_value(
            "Organisation",
            organisation,
            [
                "name",
                "org_name",
                "short_name",
                "established",
                "language",
                "phone",
                "email",
                "description",
                "registered_address",
                "registration_number",
                "website_url",
                "logo",
                "is_active",
                "country",
                "geo_l1",
                "geo_l2",
            ],
            as_dict=True,
        )

        if not organisation_data:
            return Result.not_found(
                message="Organisation profile not found."
            )

       
        organisation_data["category_l1"] = frappe.get_all(
            "Category Child Table",
            filters={
                "parent": organisation,
                "parenttype": "Organisation",
                "parentfield": "category_l1",
            },
            fields=[
                "category",
            ],
            order_by="idx asc",
        )

        
        organisation_data["category_l2"] = frappe.get_all(
            "Category Child Table",
            filters={
                "parent": organisation,
                "parenttype": "Organisation",
                "parentfield": "category_l2",
            },
            fields=[
                "category",
            ],
            order_by="idx asc",
        )

      
        organisation_data["ngo_admin"] = frappe.get_all(
            "User Child Table",
            filters={
                "parent": organisation,
                "parenttype": "Organisation",
                "parentfield": "ngo_admin",
            },
            fields=[
                "user",
                "is_active",
            ],
            order_by="idx asc",
        )

        organisation_data["id"] = organisation_data["name"]

        organisation_data.pop("name", None)

        
        profile = Organisation.model_validate(
            organisation_data
        )

        return Result.success(
            message="Organisation profile fetched successfully.",
            data=profile.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to get organisation profile.",
            data={
                "error": str(e)
            },
        )