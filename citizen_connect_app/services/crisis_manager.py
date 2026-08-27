import frappe
 
from citizen_connect_app.models.crisis import (
    Crisis,
    CrisisSummary,
)
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result
 
 
MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0
MEDIA_BASE_URL = frappe.utils.get_url()

CHILD_TABLES = {
    "media": {
        "doctype": "Media",
        "parentfield": "media",
        "fields": ["media", "caption"],
    },
    "impact": {
        "doctype": "Crisis Impact",
        "parentfield": "impact",
        "fields": ["impact_title", "impact_number", "impact_type"],
    },
    "resources_needed": {
        "doctype": "Resource Requirement",
        "parentfield": "resources_needed",
        "fields": [
            "resource_name",
            "quantity_requirement",
            "qunatity_recieved",
            "unit",
            "priority",
            "is_active",
        ],
        
    },
    "emergency_contacts": {
        "doctype": "Emergency Contacts",
        "parentfield": "emergency_contacts",
        "fields": ["agency_name", "contact_number", "agency_category"],
    },
    "collaborators": {
        "doctype": "User Child Table",
        "parentfield": "collaborators",
        "fields": ["user", "is_active"],
    },
    "donation_opportunity": {
        "doctype": "Donation Details",
        "parentfield": "donation_oppportunity",
        "fields": [
            "fund_name",
            "description",
            "external_donation_link",
            "ngo",
            "is_verified",
            "total_donation_target",
            "currency",
        ],
    },
    "volunteer_opportunity": {
        "doctype": "Child Volunteer Opportunity",
        "parentfield": "volunteer_opportunity",
        "fields": ["child_vol_opportunity", "num_of_volunteer"],
    },
}
 

def _fetch_child_rows_for_parents(
    crisis_ids, doctype, parentfield, fields
):


    grouped = {
        crisis_id: []
        for crisis_id in crisis_ids
    }

    if not crisis_ids:
        return grouped

    rows = frappe.get_all(
        doctype,
        filters={
            "parent": ["in", crisis_ids],
            "parenttype": "Crisis",
            "parentfield": parentfield,
            **({"is_active": 1} if doctype == "Resource Requirement" else {}),
            **({"is_verified": 1} if doctype == "Donation Details" else {}),
        },
        fields=["parent"] + fields,
        order_by="idx",
    )

    # Fetch Organisation names for Donation Details
    organisation_map = {}

    if doctype == "Donation Details":
        ngo_ids = [
            row["ngo"]
            for row in rows
            if row.get("ngo")
        ]

        if ngo_ids:
            organisations = frappe.get_all(
                "Organisation",
                filters={
                    "name": ["in", ngo_ids]
                },
                fields=["name", "org_name"],
            )

            organisation_map = {
                organisation["name"]: organisation["org_name"]
                for organisation in organisations
            }

    for row in rows:
        item = {
            field: row[field]
            for field in fields
        }

        if doctype == "Donation Details" and item.get("ngo"):
            item["ngo"] = organisation_map.get(
                item["ngo"],
                item["ngo"],
            )

        # Fetch Opportunity Discovery details
        if (
            doctype == "Child Volunteer Opportunity"
            and item.get("child_vol_opportunity")
        ):
            opportunity = frappe.db.get_value(
                "Opportunity Discovery",
                item["child_vol_opportunity"],
                [
                    "title",
                    "start_date",
                    "end_date",
                    "volunteer_format",
                ],
                as_dict=True,
            )

            item["title"] = (
                opportunity.get("title")
                if opportunity
                else None
            )

            item["start_date"] = (
                opportunity.get("start_date")
                if opportunity
                else None
            )

            item["end_date"] = (
                opportunity.get("end_date")
                if opportunity
                else None
            )

            item["volunteer_format"] = (
                opportunity.get("volunteer_format")
                if opportunity
                else None
            )

        # Media URL
        if doctype == "Media" and item.get("media"):
            if not item["media"].startswith(
                ("http://", "https://")
            ):
                item["media"] = (
                    f"{MEDIA_BASE_URL}{item['media']}"
                )

        grouped[row.parent].append(item)

    return grouped
 
 
def _attach_child_tables(crisis_rows, crisis_ids):
    
    for key, spec in CHILD_TABLES.items():
        grouped = _fetch_child_rows_for_parents(
            crisis_ids,
            spec["doctype"],
            spec["parentfield"],
            spec["fields"],
        )
        for crisis in crisis_rows:
            crisis[key] = grouped.get(crisis["id"], [])
 
 
def _extract_nested_location(crisis):
   
    crisis["resource_dropoff_location"] = {
        "person_name": crisis.pop("person_name", None),
        "phone_num": crisis.pop("phone_num", None),
        "time": crisis.pop("time", None),
        "location_name": crisis.pop("location_name", None),
        "location_address": crisis.pop("location_address", None),

    }
 
    crisis["location"] = {
        "country": crisis.pop("country", None),
        "geo1": crisis.pop("geography_l1", None),
        "geo2": crisis.pop("geography_l2", None),
    }
 
 
CRISIS_BASE_QUERY = """
    SELECT
        c.name AS id,
        c.title,
        c.category,
        c.description,
        c.start_date,
        c.status,
        c.crisis_summary,
 
        c.person_name,
        c.phone_num,
        c.time,
        c.location_name,
        c.location_address,
        c.verification_status,
 
        country.country_name AS country,
        g1.geo_l1 AS geography_l1,
        g2.geo_l2 AS geography_l2
 
    FROM `tabCrisis` c
 
    LEFT JOIN `tabCountry` country
        ON country.name = c.country
 
    LEFT JOIN `tabGeography L1` g1
        ON g1.name = c.geo_l1
 
    LEFT JOIN `tabGeography L2` g2
        ON g2.name = c.geo_l2
"""
 
 
def get_crisis_list(
    limit=DEFAULT_LIMIT,
    offset=DEFAULT_OFFSET,
    category=None,
    country=None,
    geography_l1=None,
    geography_l2=None,
    status="Active",
) -> Result:
    try:
        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
 
        where_clause, values = build_filters(
            category=category,
            country=country,
            geography_l1=geography_l1,
            geography_l2=geography_l2,
            status=status,
        )
 
        query = f"""
            {CRISIS_BASE_QUERY}
            {where_clause}
            ORDER BY c.creation DESC
            LIMIT %s OFFSET %s
        """
 
        values = values + [limit, offset]
 
        crisis_rows = frappe.db.sql(query, tuple(values), as_dict=True)
        crisis_ids = [crisis["id"] for crisis in crisis_rows]
 
        _attach_child_tables(crisis_rows, crisis_ids)
 
        for crisis in crisis_rows:
            _extract_nested_location(crisis)
 
        crises = [
            CrisisSummary(**crisis).model_dump()
            for crisis in crisis_rows
        ]
 
        return Result.success(
            message="Crises fetched successfully.",
            data=crises,
        )
 
    except Exception as e:
        ErrorLogger.log(e)
 
        return Result.failure(
            message="Failed to get crisis list.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback(),
                "filters": {
                    "category":category,
                    "country": country,
                    "geography_l1": geography_l1,
                    "geography_l2": geography_l2,
                    "status": status,
                },
            },
        )
 
 
def get_crisis(crisis_id) -> Result:
    try:
        query = f"""
            {CRISIS_BASE_QUERY}
            WHERE c.name = %s
        """
 
        rows = frappe.db.sql(query, (crisis_id,), as_dict=True)
 
        if not rows:
            return Result.not_found("Crisis not found.")
 
        crisis = rows[0]
 
        _attach_child_tables([crisis], [crisis_id])
        _extract_nested_location(crisis)
 
        data = Crisis(**crisis).model_dump()
 
        return Result.success(
            message="Crisis fetched successfully.",
            data=data,
        )
 
    except Exception as e:
        ErrorLogger.log(e)
 
        return Result.failure(
            message="Failed to get crisis.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback(),
                "crisis_id": crisis_id,
            },
        )
 
 
def build_filters(
    category=None,
    country=None,
    geography_l1=None,
    geography_l2=None,
    status=None,
):
    conditions = []
    values = []
 
    if country:
        conditions.append("c.country = %s")
        values.append(country)
 
    if geography_l1:
        conditions.append("c.geo_l1 = %s")
        values.append(geography_l1)
 
    if geography_l2:
        conditions.append("c.geo_l2 = %s")
        values.append(geography_l2)
 
    if status:
        conditions.append("c.status = %s")
        values.append(status)

    if category:
        conditions.append("c.category = %s")
        values.append(category)  
 
    where_clause = ""
 
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
 
    return where_clause, values