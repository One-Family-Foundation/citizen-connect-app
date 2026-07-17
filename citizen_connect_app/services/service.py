import frappe
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger


class ServiceManager:

    @staticmethod
    def get_list(
        limit=10,
        offset=0,
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
    ) -> Result:
        try:
            # Validate pagination
            limit = max(1, min(int(limit), 100))
            offset = max(0, int(offset))

            # Build filters dynamically
            filters = []
            values = []

            if category_l1:
                filters.append("l1.catalogue_name = %s")
                values.append(category_l1)
            if category_l2:
                filters.append("l2.catalogue_name = %s")
                values.append(category_l2)            
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

                    s.gender,
                    s.income,
                    s.age,

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
                    s.eligibility_condition,
                    s.rating,

                    s.ngo_org AS ngo_id,
                    org.org_name AS ngo_name,

                    l1.catalogue_name AS l1_name,
                    l2.catalogue_name AS l2_name
                FROM `tabService` s
                LEFT JOIN `tabOrganisation` org
                    ON org.name = s.ngo_org
                LEFT JOIN `tabGeography L1` geo1
                    ON geo1.name = s.service_geo1
                LEFT JOIN `tabGeography L2` geo2
                    ON geo2.name = s.service_geo2
                LEFT JOIN `tabService Category` selected_category
                    ON selected_category.name = s.service_category
                LEFT JOIN `tabService Category` l1
                    ON l1.lft <= selected_category.lft
                    AND l1.rgt >= selected_category.rgt
                    AND l1.category_level = 'L1'
                LEFT JOIN `tabService Category` l2
                    ON l2.lft <= selected_category.lft
                    AND l2.rgt >= selected_category.rgt
                    AND l2.category_level = 'L2'
                {where_clause}
                ORDER BY s.creation DESC
                LIMIT %s OFFSET %s
                """,
                values,
                as_dict=True,
            )

            # Transform response
            for service in services:
                # Location
                location = {}

                if service.get("service_country"):
                    location["country"] = service.pop("service_country")

                if service.get("service_geo1"):
                    location["geo1"] = service.pop("service_geo1")

                if service.get("service_geo2"):
                    location["geo2"] = service.pop("service_geo2")

                service["location"] = location

                # Service Category Hierarchy
                service["service_category"] = {
                    "l1": {"name": service.pop("l1_name")},
                    "l2": {"name": service.pop("l2_name")},
                }

            return Result.success( {
                "services": services,
                "limit": limit,
                "offset": offset,
                "has_more": len(services) == limit,
               }
            )
        except Exception as e:
            ErrorLogger.log(
                message="Failed to fetch services",
                details=str(e),
                stacktrace=frappe.get_traceback(),
            )
            raise


    @staticmethod
    def get_categories():
        try:
            rows = frappe.db.sql(
                """
                SELECT
                    l1.name AS l1_id,
                    l1.catalogue_name AS l1_name,
                    l2.name AS l2_id,
                    l2.catalogue_name AS l2_name
                FROM `tabService Category` l1
                LEFT JOIN `tabService Category` l2
                    ON l2.parent_service_category = l1.name
                    AND l2.category_level = 'L2'
                WHERE l1.category_level = 'L1'
                ORDER BY l1.catalogue_name, l2.catalogue_name;
                """,
                as_dict=True,
            )

            categories = {}

            for row in rows:
                if row.l1_id not in categories:
                    categories[row.l1_id] = {
                        "id": row.l1_id,
                        "name": row.l1_name,
                        "children": [],
                    }

                if row.l2_id:
                    categories[row.l1_id]["children"].append(
                        {"id": row.l2_id, "name": row.l2_name}
                    )

            return Result.success({"categories": list(categories.values())})
            
        except Exception as e:
            ErrorLogger.log(
                message="Failed to fetch categories",
                details=str(e),
                stacktrace=frappe.get_traceback(),
            )
            raise