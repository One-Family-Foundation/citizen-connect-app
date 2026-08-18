import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class ServiceManager:

    CATEGORIES_CACHE_KEY = "service_categories_v1"

    @staticmethod
    def get_list(
        limit=10,
        offset=0,
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
        lang="en",
    ) -> Result:
        try:
            # Validate pagination parameters
            limit = max(1, min(int(limit), 100))
            offset = max(0, int(offset))

            # Build filters dynamically
            filters = []
            values = []

            # Category filters
            if category_l2:
                # Exact L2 match
                filters.append("s.category_l2 = %s")
                values.append(category_l2)

            elif category_l1:
                # All L2s under the selected L1
                filters.append("s.category_l1 = %s")
                values.append(category_l1)
            if country:
                filters.append("geo1.country_name = %s")
                values.append(country)
            if geo1:
                filters.append("geo1.geo_l1 = %s")
                values.append(geo1)
            if geo2:
                filters.append("geo2.geo_2 = %s")
                values.append(geo2)

            where_clause = ""
            if filters:
                where_clause = "WHERE " + " AND ".join(filters)

            values.extend([limit, offset])

            services = frappe.db.sql(
                    f"""
                    SELECT
                        s.name AS id,
                        s.title,
                        s.description,
                        s.service_country,
                        geo1.geo_l1 AS service_geo1,
                        geo2.geo_2 AS service_geo2,
                        s.cost_model,
                        s.cost_details,
                        s.sponsorship_information,
                        s.availability_status,
                        s.service_channel,
                        s.service_status,
                        s.creation,
                        s.modified,
                        s.eligibility_condition,
                        s.contact_number,
                        s.email,
                        s.whatsapp_number,
                        s.rating,
                        s.ngo_org AS ngo_name,
                        

                        s.category_l1 AS l1_name,
                        s.category_l2 AS l2_name
                        

                    FROM `tabService` s

                    LEFT JOIN `tabGeography L1` geo1
                        ON geo1.name = s.service_geo1

                    LEFT JOIN `tabGeography L2` geo2
                        ON geo2.name = s.service_geo2

                    

                    {where_clause}

                    ORDER BY s.modified DESC
                    LIMIT %s OFFSET %s
                    """,
                    values,
                    as_dict=True,
                )
            frappe.local.lang = lang
            # Transform raw rows into domain objects
            service_list = []
            for row in services:
                service = ServiceManager._create_service(row)
                service_list.append(service)

            return Result.success(
                message="Services fetched successfully.",
                data={
                    "services": service_list,
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(service_list) == limit,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)
            raise

    @staticmethod
    def get(service_id: str) -> Result:
        try:
            service = frappe.db.sql(
                """
                SELECT
                    s.name AS id,
                    s.title,
                    s.description,
                    s.service_country,
                    geo1.geo_l1 AS service_geo1,
                    geo2.geo_2 AS service_geo2,
                    s.cost_model,
                    s.cost_details,
                    s.sponsorship_information,
                    s.availability_status,
                    s.service_channel,
                    s.service_status,
                    s.creation,
                    s.modified,
                    s.contact_number,
                    s.email,
                    s.whatsapp_number,
                    s.eligibility_condition,
                    s.rating,
                    s.ngo_org AS ngo_name,

                    l2.parent_category AS l1_name,
                    s.service_category AS l2_name

                FROM `tabService` s

                LEFT JOIN `tabGeography L1` geo1
                    ON geo1.name = s.service_geo1

                LEFT JOIN `tabGeography L2` geo2
                    ON geo2.name = s.service_geo2

                LEFT JOIN `tabCategory` l2
                    ON l2.name = s.service_category

                WHERE s.name = %s
                """,
                (service_id,),
                as_dict=True,
            )

            if not service:
                return Result.not_found(message="Service not found.")

            row = service[0]
            service_data = ServiceManager._create_service(row)

            return Result.success(
                message="Service fetched successfully.",
                data=service_data,
            )
        except Exception as e:
            ErrorLogger.log(e)
            raise
    @staticmethod
    def _create_service(row: dict) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "location": {
                "country": row["service_country"],
                "geo1": row["service_geo1"],
                "geo2": row["service_geo2"],
            },
            "cost_model": row["cost_model"],
            "cost_details": row["cost_details"],
            "sponsorship_information": row["sponsorship_information"],
            "availability_status": row["availability_status"],
            "service_channel": row["service_channel"],
            "service_status": row["service_status"],
            "creation": row["creation"],
            "modified": row["modified"],
            "eligibility_condition": row["eligibility_condition"],
            "rating": row["rating"],
            "ngo_name": row["ngo_name"],
            "mobile_number": row["contact_number"],
            "email_id":row["email"],
            "whatsapp_mobile_number":row["whatsapp_number"],
            "service_category": {
                "l1": {"name":row["l1_name"],"display_name": frappe._(row["l1_name"])},
                "l2": {"name": row["l2_name"],"display_name": frappe._(row["l2_name"])},
            },
        }

    @staticmethod
    def get_categories() -> Result:
        cache = frappe.cache()

        try:
            cached_data = cache.get_value(ServiceManager.CATEGORIES_CACHE_KEY)
            if cached_data:
                frappe.logger().info("Locations API: Cache Hit")
                return Result.success(
                    message="Services fetched successfully.",
                    data=cached_data,
                )

            rows = frappe.db.sql(
                """
                SELECT
                    l1.name AS l1_id,
                    l1.catalogue_name AS l1_name,
                    l2.name AS l2_id,
                    l2.catalogue_name AS l2_name
                FROM `tabCategory` l1
                LEFT JOIN `tabCategory` l2
                    ON l2.parent_category = l1.name
                    AND l2.category_level = 'L2'
                WHERE l1.category_level = 'L1'
                ORDER BY l1.catalogue_name, l2.catalogue_name;
                """,
                as_dict=True,
            )

            categories = {}
            for row in rows:
                l1_id = row["l1_id"]
                if l1_id not in categories:
                    categories[l1_id] = {
                        "id": l1_id,
                        "name": row["l1_name"],
                        "children": [],
                    }

                if row["l2_id"]:
                    categories[l1_id]["children"].append(
                        {"id": row["l2_id"], "name": row["l2_name"]}
                    )

            response = {"categories": list(categories.values())}
            cache.set_value(
                ServiceManager.CATEGORIES_CACHE_KEY,
                response,
                expires_in_sec=3600,
            )
            return Result.success(
                message="Services Fetched successfully", data=response
            )

        except Exception as e:
            ErrorLogger.log(e)
            raise

def clear_categories_cache(doc=None, method=None):
    frappe.cache().delete_value(ServiceManager.CATEGORIES_CACHE_KEY)