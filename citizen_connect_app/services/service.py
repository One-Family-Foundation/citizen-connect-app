import frappe
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger


class ServiceManager:

    @staticmethod
    def get_list(limit=10, offset=0) -> Result:
        try:
            # Validate pagination
            limit = max(1, min(int(limit), 100))
            offset = max(0, int(offset))

            services = frappe.db.sql("""
                SELECT
                    s.name AS id,
                    s.title,
                    s.description,
                    s.conditions,
                    s.cost_model,
                    s.cost_details,
                    s.sponsorship_information,
                    s.availability_status,
                    s.service_channel,
                    s.service_status,
                    s.creation,

                    s.ngo_org AS ngo_id,
                    org.org_name AS ngo_name,

                    l4.name AS service_category_id,
                    l4.catalogue_name AS service_category_name,
                    l4.category_level

                FROM `tabService` s

                LEFT JOIN `tabOrganisation` org
                    ON org.name = s.ngo_org

                LEFT JOIN `tabService Category` root
                    ON root.name = s.service_category

                LEFT JOIN `tabService Category` l4
                    ON l4.lft BETWEEN root.lft AND root.rgt
                    AND l4.category_level = 'L4'

                ORDER BY s.creation DESC
                LIMIT %s OFFSET %s
            """, (limit, offset), as_dict=True)

            return {
                    "services": services,
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(services) == limit
                }
            

        except Exception :
            ErrorLogger.log(
                message="Failed to fetch services",
                details=str(e),
                stacktrace=frappe.get_traceback()
            )
            raise
