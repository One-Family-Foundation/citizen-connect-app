# import frappe

# from citizen_connect_app.models.crisis import (
#     Crisis,
#     CrisisSummary,
# )
# from citizen_connect_app.utils.error_logger import ErrorLogger
# from samaaja.utils.result import Result


# MIN_LIMIT = 1
# MAX_LIMIT = 100
# DEFAULT_LIMIT = 10
# DEFAULT_OFFSET = 0


# def get_crisis_list(
#     limit=DEFAULT_LIMIT,
#     offset=DEFAULT_OFFSET,
#     country=None,
#     geography_l1=None,
#     geography_l2=None,
#     status="Active",
# ) -> Result:
#     try:
#         limit = max(
#             MIN_LIMIT,
#             min(int(limit), MAX_LIMIT),
#         )

#         offset = max(
#             0,
#             int(offset),
#         )

#         where_clause, values = build_filters(
#             country=country,
#             geography_l1=geography_l1,
#             geography_l2=geography_l2,
#             status=status,
#         )

#         query = f"""
#             SELECT
#                 c.name AS id,
#                 c.title,
#                 c.description,
#                 c.start_date,
#                 c.status,
#                 c.crisis_summary,
#                 c.verification_status,

#                 c.person_name,
#                 c.phone_num,
#                 c.time,
#                 c.location AS dropoff_location,

#                 country.country_name AS country,
#                 g1.geo_l1 AS geography_l1,
#                 g2.geo_2 AS geography_l2

#             FROM `tabCrisis` c

#             LEFT JOIN `tabCountry` country
#                 ON country.name = c.country

#             LEFT JOIN `tabGeography L1` g1
#                 ON g1.name = c.geo_l1

#             LEFT JOIN `tabGeography L2` g2
#                 ON g2.name = c.geo_l2

#             {where_clause}

#             ORDER BY c.creation DESC

#             LIMIT %s OFFSET %s
#         """

#         values.extend([
#             limit,
#             offset,
#         ])

#         crisis_rows = frappe.db.sql(
#             query,
#             tuple(values),
#             as_dict=True,
#         )

#         crisis_ids = [
#             crisis["id"]
#             for crisis in crisis_rows
#         ]

#         media_map = {}

#         if crisis_ids:
#             media_rows = frappe.get_all(
#                 "Media",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "media",
#                 },
#                 fields=[
#                     "parent",
#                     "media",
#                     "caption",
#                 ],
#                 order_by="idx",
#             )

#             for row in media_rows:
#                 media_map.setdefault(row.parent, []).append({
#                     "media": row.media,
#                     "caption": row.caption,
#                 })

#         impact_map = {}

#         if crisis_ids:
#             impact_rows = frappe.get_all(
#                 "Crisis Impact",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "impact",
#                 },
#                 fields=[
#                     "parent",
#                     "impact_title",
#                     "impact_number",
#                     "impact_type",
#                 ],
#                 order_by="idx",
#             )

#             for row in impact_rows:
#                 impact_map.setdefault(row.parent, []).append({
#                     "impact_title": row.impact_title,
#                     "impact_number": row.impact_number,
#                     "impact_type": row.impact_type,
#                 })


#         resources_map = {}

#         if crisis_ids:
#             resource_rows = frappe.get_all(
#                 "Resource Requirement",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "resources_needed",
#                 },
#                 fields=[
#                     "parent",
#                     "resource_name",
#                     "quantity_requirement",
#                     "qunatity_recieved",
#                     "unit",
#                     "priority",
#                     "is_verified",
#                 ],
#                 order_by="idx",
#             )

#             for row in resource_rows:
#                 resources_map.setdefault(row.parent, []).append({
#                     "resource_name": row.resource_name,
#                     "quantity_requirement": row.quantity_requirement,
#                     "qunatity_recieved": row.qunatity_recieved,
#                     "unit": row.unit,
#                     "priority": row.priority,
#                     "is_verified": row.is_verified,
#                 })


#         contacts_map = {}

#         if crisis_ids:
#             contact_rows = frappe.get_all(
#                 "Emergency Contacts",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "emergency_contacts",
#                 },
#                 fields=[
#                     "parent",
#                     "agency_name",
#                     "contact_number",
#                     "agency_category",
#                 ],
#                 order_by="idx",
#             )

#             for row in contact_rows:
#                 contacts_map.setdefault(row.parent, []).append({
#                     "agency_name": row.agency_name,
#                     "contact_number": row.contact_number,
#                     "agency_category": row.agency_category,
#                 })


#         collaborators_map = {}

#         if crisis_ids:
#             collaborator_rows = frappe.get_all(
#                 "User Child Table",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "collaborators",
#                 },
#                 fields=[
#                     "parent",
#                     "user",
#                     "is_active",
#                 ],
#                 order_by="idx",
#             )

#             for row in collaborator_rows:
#                 collaborators_map.setdefault(row.parent, []).append({
#                     "user": row.user,
#                     "is_active": row.is_active,
#                 })

#         donation_map = {}

#         if crisis_ids:
#             donation_rows = frappe.get_all(
#                 "Donation Details",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "donation_oppportunity",
#                 },
#                 fields=[
#                     "parent",
#                     "fund_name",
#                     "description",
#                     "external_donation_link",
#                     "ngo",
#                     "is_verified",
#                     "total_donation_target",
#                 ],
#                 order_by="idx",
#             )

#             for row in donation_rows:
#                 donation_map.setdefault(row.parent, []).append({
#                     "fund_name": row.fund_name,
#                     "description": row.description,
#                     "external_donation_link": row.external_donation_link,
#                     "ngo": row.ngo,
#                     "is_verified": row.is_verified,
#                     "total_donation_target": row.total_donation_target,
#                 })

#         volunteer_map = {}

#         if crisis_ids:
#             volunteer_rows = frappe.get_all(
#                 "Child Volunteer Opportunity",
#                 filters={
#                     "parent": ["in", crisis_ids],
#                     "parenttype": "Crisis",
#                     "parentfield": "volunteer_opportunity",
#                 },
#                 fields=[
#                     "parent",
#                     "child_vol_opportunity",
#                     "num_of_volunteer",
#                 ],
#                 order_by="idx",
#             )

#             for row in volunteer_rows:
#                 volunteer_map.setdefault(row.parent, []).append({
#                     "child_vol_opportunity": row.child_vol_opportunity,
#                     "num_of_volunteer": row.num_of_volunteer,
#                 })

#         for crisis in crisis_rows:
#             crisis["media"] = media_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["impact"] = impact_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["resources_needed"] = resources_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["emergency_contacts"] = contacts_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["collaborators"] = collaborators_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["donation_opportunity"] = donation_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["volunteer_opportunity"] = volunteer_map.get(
#                 crisis["id"],
#                 [],
#             )

#             crisis["resource_dropoff_location"] = {
#                 "person_name": crisis.pop("person_name"),
#                 "phone_num": crisis.pop("phone_num"),
#                 "time": crisis.pop("time"),
#                 "location": crisis.pop("dropoff_location"),
#             }

#             crisis["location"] = {
#                 "country": crisis.pop("country"),
#                 "geo1": crisis.pop("geography_l1"),
#                 "geo2": crisis.pop("geography_l2"),
#             }


#         crises = [
#             CrisisSummary(
#                 **crisis
#             ).model_dump()
#             for crisis in crisis_rows
#         ]

#         return Result.success(
#             message="Crises fetched successfully.",
#             data=crises,
#         )

#     except Exception as e:
#         ErrorLogger.log(e)

#         return Result.failure(
#             message="Failed to get crisis list.",
#             data={
#                 "error": str(e),
#             },
#             error_data={
#                 "traceback": frappe.get_traceback(),
#             },
#         )


# def get_crisis(crisis_id) -> Result:
#     try:
#         query = """
#             SELECT
#                 c.name AS id,
#                 c.title,
#                 c.description,
#                 c.start_date,
#                 c.status,
#                 c.crisis_summary,
#                 c.verification_status,

#                 c.person_name,
#                 c.phone_num,
#                 c.time,
#                 c.location AS dropoff_location,

#                 country.country_name AS country,
#                 g1.geo_l1 AS geography_l1,
#                 g2.geo_2 AS geography_l2

#             FROM `tabCrisis` c

#             LEFT JOIN `tabCountry` country
#                 ON country.name = c.country

#             LEFT JOIN `tabGeography L1` g1
#                 ON g1.name = c.geo_l1

#             LEFT JOIN `tabGeography L2` g2
#                 ON g2.name = c.geo_l2

#             WHERE c.name = %s
#         """

#         rows = frappe.db.sql(
#             query,
#             (crisis_id,),
#             as_dict=True,
#         )

#         if not rows:
#             return Result.not_found(
#                 "Crisis not found."
#             )

#         crisis = rows[0]
#         media_rows = frappe.get_all(
#             "Media",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "media",
#             },
#             fields=[
#                 "media",
#                 "caption",
#             ],
#             order_by="idx",
#         )

#         crisis["media"] = [
#             {
#                 "media": row.media,
#                 "caption": row.caption,
#             }
#             for row in media_rows
#         ]

#         # --------------------------------
#         # Crisis Impact
#         # --------------------------------

#         impact_rows = frappe.get_all(
#             "Crisis Impact",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "impact",
#             },
#             fields=[
#                 "impact_title",
#                 "impact_number",
#                 "impact_type",
#             ],
#             order_by="idx",
#         )

#         crisis["impact"] = [
#             {
#                 "impact_title": row.impact_title,
#                 "impact_number": row.impact_number,
#                 "impact_type": row.impact_type,
#             }
#             for row in impact_rows
#         ]

#         # --------------------------------
#         # Resources
#         # --------------------------------

#         resource_rows = frappe.get_all(
#             "Resource Requirement",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "resources_needed",
#             },
#             fields=[
#                 "resource_name",
#                 "quantity_requirement",
#                 "qunatity_recieved",
#                 "unit",
#                 "priority",
#                 "is_verified",
#             ],
#             order_by="idx",
#         )

#         crisis["resources_needed"] = [
#             {
#                 "resource_name": row.resource_name,
#                 "quantity_requirement": row.quantity_requirement,
#                 "qunatity_recieved": row.qunatity_recieved,
#                 "unit": row.unit,
#                 "priority": row.priority,
#                 "is_verified": row.is_verified,
#             }
#             for row in resource_rows
#         ]

#         contact_rows = frappe.get_all(
#             "Emergency Contacts",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "emergency_contacts",
#             },
#             fields=[
#                 "agency_name",
#                 "contact_number",
#                 "agency_category",
#             ],
#             order_by="idx",
#         )

#         crisis["emergency_contacts"] = [
#             {
#                 "agency_name": row.agency_name,
#                 "contact_number": row.contact_number,
#                 "agency_category": row.agency_category,
#             }
#             for row in contact_rows
#         ]

#         collaborator_rows = frappe.get_all(
#             "User Child Table",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "collaborators",
#             },
#             fields=[
#                 "user",
#                 "is_active",
#             ],
#             order_by="idx",
#         )

#         crisis["collaborators"] = [
#             {
#                 "user": row.user,
#                 "is_active": row.is_active,
#             }
#             for row in collaborator_rows
#         ]

#         donation_rows = frappe.get_all(
#             "Donation Details",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "donation_oppportunity",
#             },
#             fields=[
#                 "fund_name",
#                 "description",
#                 "external_donation_link",
#                 "ngo",
#                 "is_verified",
#                 "total_donation_target",
#             ],
#             order_by="idx",
#         )

#         crisis["donation_opportunity"] = [
#             {
#                 "fund_name": row.fund_name,
#                 "description": row.description,
#                 "external_donation_link": row.external_donation_link,
#                 "ngo": row.ngo,
#                 "is_verified": row.is_verified,
#                 "total_donation_target": row.total_donation_target,
#             }
#             for row in donation_rows
#         ]

#         volunteer_rows = frappe.get_all(
#             "Child Volunteer Opportunity",
#             filters={
#                 "parent": crisis_id,
#                 "parenttype": "Crisis",
#                 "parentfield": "volunteer_opportunity",
#             },
#             fields=[
#                 "child_vol_opportunity",
#                 "num_of_volunteer",
#             ],
#             order_by="idx",
#         )

#         crisis["volunteer_opportunity"] = [
#             {
#                 "child_vol_opportunity": row.child_vol_opportunity,
#                 "num_of_volunteer": row.num_of_volunteer,
#             }
#             for row in volunteer_rows
#         ]

#         crisis["resource_dropoff_location"] = {
#             "person_name": crisis.pop("person_name"),
#             "phone_num": crisis.pop("phone_num"),
#             "time": crisis.pop("time"),
#             "location": crisis.pop("dropoff_location"),
#         }

#         crisis["location"] = {
#             "country": crisis.pop("country"),
#             "geo1": crisis.pop("geography_l1"),
#             "geo2": crisis.pop("geography_l2"),
#         }

#         data = Crisis(
#             **crisis
#         ).model_dump()

#         return Result.success(
#             message="Crisis fetched successfully.",
#             data=data,
#         )

#     except Exception as e:
#         ErrorLogger.log(e)

#         return Result.failure(
#             message="Failed to get crisis.",
#             data={
#                 "error": str(e),
#             },
#             error_data={
#                 "traceback": frappe.get_traceback(),
#             },
#         )


# def build_filters(
#     country=None,
#     geography_l1=None,
#     geography_l2=None,
#     status=None,
# ):
#     conditions = []
#     values = []

#     if country:
#         conditions.append(
#             "c.country = %s"
#         )
#         values.append(country)

#     if geography_l1:
#         conditions.append(
#             "c.geo_l1 = %s"
#         )
#         values.append(geography_l1)

#     if geography_l2:
#         conditions.append(
#             "c.geo_l2 = %s"
#         )
#         values.append(geography_l2)

#     if status:
#         conditions.append(
#             "c.status = %s"
#         )
#         values.append(status)

#     where_clause = ""

#     if conditions:
#         where_clause = (
#             "WHERE "
#             + " AND ".join(conditions)
#         )

#     return where_clause, values

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
 
# Each child table Crisis has, described once. Both get_crisis_list and
# get_crisis pull from this so the two views can't drift out of sync.
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
            "is_verified",
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
        ],
    },
    "volunteer_opportunity": {
        "doctype": "Child Volunteer Opportunity",
        "parentfield": "volunteer_opportunity",
        "fields": ["child_vol_opportunity", "num_of_volunteer"],
    },
}
 
 
def _fetch_child_rows_for_parents(crisis_ids, doctype, parentfield, fields):
    """Fetch one child table's rows for many parents at once, grouped by parent id."""
    grouped = {crisis_id: [] for crisis_id in crisis_ids}
 
    if not crisis_ids:
        return grouped
 
    rows = frappe.get_all(
        doctype,
        filters={
            "parent": ["in", crisis_ids],
            "parenttype": "Crisis",
            "parentfield": parentfield,
        },
        fields=["parent"] + fields,
        order_by="idx",
    )
 
    for row in rows:
        grouped[row.parent].append({field: row[field] for field in fields})
 
    return grouped
 
 
def _attach_child_tables(crisis_rows, crisis_ids):
    """Mutates crisis_rows in place, attaching every child table by key."""
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
    """Pulls the flat SQL columns for dropoff/location into their nested shape.
 
    Uses .pop(key, None) rather than bare pops so a column rename in the SQL
    surfaces as a None value here instead of a hard KeyError deep in a request.
    """
    crisis["resource_dropoff_location"] = {
        "person_name": crisis.pop("person_name", None),
        "phone_num": crisis.pop("phone_num", None),
        "time": crisis.pop("time", None),
        "location": crisis.pop("dropoff_location", None),
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
        c.description,
        c.start_date,
        c.status,
        c.crisis_summary,
        c.verification_status,
 
        c.person_name,
        c.phone_num,
        c.time,
        c.location AS dropoff_location,
 
        country.country_name AS country,
        g1.geo_l1 AS geography_l1,
        g2.geo_2 AS geography_l2
 
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
    country=None,
    geography_l1=None,
    geography_l2=None,
    status="Active",
) -> Result:
    try:
        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
 
        where_clause, values = build_filters(
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
 
    where_clause = ""
 
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
 
    return where_clause, values