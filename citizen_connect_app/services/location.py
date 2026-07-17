import frappe
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result  # Note: ensure your custom result class handles capitalization


class LocationManager:

    @staticmethod
    def get_locations():
        try:
            # 1. Fetch all records in bulk to avoid the N+1 query problem
            countries = frappe.get_all(
                "Country", 
                fields=["name", "country_name"]
            )
            geo_l1_records = frappe.get_all(
                "Geography L1", 
                fields=["name", "geo_l1", "country_name"]
            )
            geo_l2_records = frappe.get_all(
                "Geography L2", 
                fields=["name", "geo_2", "geo_l1"]
            )

            # 2. Map Geography L2 items to their respective Geography L1 parents
            l2_by_l1 = {}
            for l2 in geo_l2_records:
                l2_by_l1.setdefault(l2.geo_l1, []).append({
                    "id": l2.name,
                    "name": l2.geo_2
                })

            # 3. Map Geography L1 items (with their L2 children) to their Countries
            l1_by_country = {}
            for l1 in geo_l1_records:
                l1_by_country.setdefault(l1.country_name, []).append({
                    "id": l1.name,
                    "name": l1.geo_l1,
                    "geo_l2": l2_by_l1.get(l1.name, [])
                })

            # 4. Construct the final structured response
            locations = [
                {
                    "id": country.name,
                    "name": country.country_name,
                    "geo_l1": l1_by_country.get(country.name, [])
                }
                for country in countries
            ]

            # Fix: Using 'result' exactly as imported
            return Result.success(
                message="Locations fetched successfully",
                data={"locations": locations}
            )

        except Exception as e:
            # It's good practice to log the actual exception details
            ErrorLogger.log_error(e)
            return result.failure(
                message="Failed to fetch locations",
                error=str(e)
            )