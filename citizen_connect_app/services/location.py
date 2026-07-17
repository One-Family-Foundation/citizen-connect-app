import frappe
from citizen_connect_app.utils.error_logger import ErrorLogger


class LocationManager:

    @staticmethod
    def get_locations():
        try:
            countries = frappe.get_all(
                "Country",
                fields=["name", "country_name"]
            )

            locations = []

            for country in countries:
                geo_l1_list = frappe.get_all(
                    "Geography L1",
                    filters={"country_name": country.name},
                    fields=["name", "geo_l1"]
                )

                geo_l1_response = []

                for geo1 in geo_l1_list:
                    geo_l2_list = frappe.get_all(
                        "Geography L2",
                        filters={"geo_l1": geo1.name},
                        fields=["name", "geo_2"]
                    )

                    geo_l1_response.append({
                        "id": geo1.name,
                        "name": geo1.geo_l1,
                        "geo_l2": [
                            {
                                "id": geo2.name,
                                "name": geo2.geo_2
                            }
                            for geo2 in geo_l2_list
                        ]
                    })

                locations.append({
                    "id": country.name,
                    "name": country.country_name,
                    "geo_l1": geo_l1_response
                })

            return locations

        except Exception as e:
            ErrorLogger.log_error(
                title="Location Fetch Error",
                error=e,
                reference_doctype="Country"
            )
            raise