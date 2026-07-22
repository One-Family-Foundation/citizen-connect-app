import frappe
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result  


class LocationManager:
    CACHE_KEY = "locations_api_v1"

    @staticmethod
    def get_locations():
        cache = frappe.cache()
        try:
            cached_data = cache.get_value(LocationManager.CACHE_KEY)
            if cached_data:
                frappe.logger().info("Locations API: Cache Hit")
                return Result.success(
                    message="Locations fetched successfully",
                    data=cached_data
                )
            frappe.logger().info("Locations API: Cache Miss")
            
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

            l2_by_l1 = {}
            for l2 in geo_l2_records:
                l2_by_l1.setdefault(l2.geo_l1, []).append({
                    "id": l2.name,
                    "name": l2.geo_2
                })

            l1_by_country = {}
            for l1 in geo_l1_records:
                l1_by_country.setdefault(l1.country_name, []).append({
                    "id": l1.name,
                    "name": l1.geo_l1,
                    "geo_l2": l2_by_l1.get(l1.name, [])
                })

     
            locations = [
                {
                    "id": country.name,
                    "name": country.country_name,
                    "geo_l1": l1_by_country.get(country.name, [])
                }
                for country in countries
            ]

            
            response ={
                "locations":locations
            }
            cache.set_value(
                LocationManager.CACHE_KEY,
                response,
                expires_in_sec=3600
            )
            return Result.success(
                message="Locations fetched successfully",
                data=response
            )

        except Exception as e:
            ErrorLogger.log_error(e)
            return Result.failure(
                message="Failed to fetch locations",
                error=str(e)
            )
    @staticmethod
    def clear_cache():
        """Clear location cache manually."""
        frappe.cache().delete_value(LocationManager.CACHE_KEY)    