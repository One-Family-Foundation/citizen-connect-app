import frappe

from citizen_connect_app.models.volunteer_opportunity import (
    Opportunity,
    OpportunitySummary,
    Skill
)
from citizen_connect_app.models.ngo import NGO
from citizen_connect_app.models.utils import Location, Category
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class OpportunityManager:

    MIN_LIMIT = 1
    MAX_LIMIT = 100
    DEFAULT_LIMIT = 10
    DEFAULT_OFFSET = 0

    _SELECT_FIELDS = """
        o.name AS id,
        o.title,
        o.description,
        o.crisis_link,

        o.category_l1 AS category_l1_name,
        o.category_l2 AS category_l2_name,
        o.language,
        c.name AS country,
        g1.geo_l1,
        g2.geo_2,

        o.volunteer_format,
        o.expected_time,
        o.start_date,
        o.end_date,
        o.compensation_type,

        org.name AS ngo_id,
        org.org_name AS ngo_name,
        org.phone,
        org.email,

        o.rating_uimw AS rating,
        o.status,

        o.creation,
        o.modified
    """

    _JOINS = """
        FROM `tabOpportunity Discovery` o
        
        LEFT JOIN `tabCountry` c
            ON c.name = o.country

        LEFT JOIN `tabGeography L1` g1
            ON g1.name = o.geo_l1

        LEFT JOIN `tabGeography L2` g2
            ON g2.name = o.geo_l2

        LEFT JOIN `tabOrganisation` org
            ON org.name = o.ngo
    """

    @staticmethod
    def get_list(
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
        volunteer_format=None,
        compensation_type=None,
        status="Active",
    ):

        try:

            limit = max(
                OpportunityManager.MIN_LIMIT,
                min(int(limit), OpportunityManager.MAX_LIMIT),
            )
            offset = max(0, int(offset))

            where_clause, values = OpportunityManager._build_filters(
                category_l1=category_l1,
                category_l2=category_l2,
                country=country,
                geo1=geo1,
                geo2=geo2,
                volunteer_format=volunteer_format,
                compensation_type=compensation_type,
                status=status,
            )

            values.extend([limit, offset])

            query = f"""
                SELECT
                    {OpportunityManager._SELECT_FIELDS}
                {OpportunityManager._JOINS}
                {where_clause}
                ORDER BY o.modified DESC
                LIMIT %s OFFSET %s
            """

            rows = frappe.db.sql(query, values, as_dict=True)

            opportunities = [
                OpportunityManager._create_summary(row).model_dump()
                for row in rows
            ]

            return Result.success(
                message="Volunteer opportunities fetched successfully.",
                data={
                    "opportunities": opportunities,
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(opportunities) == limit,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)
            raise

    @staticmethod
    def get(opportunity_id):

        try:

            query = f"""
                SELECT
                    {OpportunityManager._SELECT_FIELDS}
                {OpportunityManager._JOINS}
                WHERE o.name=%s
            """

            rows = frappe.db.sql(query, (opportunity_id,), as_dict=True)

            if not rows:
                return Result.not_found("Volunteer opportunity not found.")

            return Result.success(
                message="Volunteer opportunity fetched successfully.",
                data=OpportunityManager._create(rows[0]).model_dump(),
            )

        except Exception as e:
            ErrorLogger.log(e)
            raise

    @staticmethod
    def _build_filters(
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
        volunteer_format=None,
        compensation_type=None,
        status=None,
    ):

        filters = []
        values = []

        if category_l1:
            filters.append("o.category_l1=%s")
            values.append(category_l1)

        if category_l2:
            filters.append("o.category_l2=%s")
            values.append(category_l2)

        if country:
            filters.append("c.name=%s")
            values.append(country)

        if geo1:
            filters.append("g1.geo_l1=%s")
            values.append(geo1)

        if geo2:
            filters.append("g2.geo_2=%s")
            values.append(geo2)

        if volunteer_format:
            filters.append("o.volunteer_format=%s")
            values.append(volunteer_format)

        if compensation_type:
            filters.append("o.compensation_type=%s")
            values.append(compensation_type)

        if status:
            filters.append("o.status=%s")
            values.append(status)

        where = ""

        if filters:
            where = "WHERE " + " AND ".join(filters)

        return where, values
    @staticmethod
    def _get_skills(opportunity_id):
        rows = frappe.get_all(
            "Skill",
            filters={
               "parent": opportunity_id,
               "parenttype": "Opportunity Discovery",
               "parentfield": "skills",
            },
           fields=["skill_name"],
           order_by="idx",
        )

        return [ Skill(skill_name=row["skill_name"])for row in rows ]
    
    @staticmethod
    def _create_summary(row):

        return OpportunitySummary(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            location=Location(
                country=row["country"],
                geo1=row["geo_l1"],
                geo2=row["geo_2"],
            ),
            volunteer_format=row["volunteer_format"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            compensation_type=row["compensation_type"],
            rating=row["rating"],
            status=row["status"],
            creation=row["creation"],
            modified=row["modified"],
            category=Category(
                l1=row["category_l1_name"],
                l2=row["category_l2_name"],
            ),
            language=row["language"],
        )

    @staticmethod
    def _create(row):

        ngo = None

        if row["ngo_id"]:
            ngo = NGO(
                id=row["ngo_id"],
                name=row["ngo_name"],
                phone=row["phone"],
                email=row["email"],
            )
        skills = OpportunityManager._get_skills(row["id"])

        return Opportunity(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            skills=skills,
            crisis_link=row["crisis_link"],
            location=Location(
                country=row["country"],
                geo1=row["geo_l1"],
                geo2=row["geo_2"],
            ),
            volunteer_format=row["volunteer_format"],
            expected_time=row["expected_time"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            compensation_type=row["compensation_type"],
            ngo=ngo,
            rating=row["rating"],
            status=row["status"],
            creation=row["creation"],
            modified=row["modified"],
            category=Category(
                l1=row["category_l1_name"],
                l2=row["category_l2_name"],
            ),
            language=row["language"],
        )