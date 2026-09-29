import frappe
from citizen_connect_app.models.scheme import Scheme, SchemeSummary
from citizen_connect_app.models.ngo import NGO
from citizen_connect_app.models.utils import LocationResponse, CategoryResponse
from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class SchemeManager:
    """Data access layer for the Scheme doctype."""

    MIN_LIMIT = 1
    MAX_LIMIT = 100
    DEFAULT_LIMIT = 10
    DEFAULT_OFFSET = 0

    _SELECT_FIELDS = """
        s.name AS id,
        s.scheme_name,
        s.description,
        s.status,
        s.benefit,
        s.eligibility,
        s.documents_required,
        s.application_url,
        s.category_l1 AS category_l1_name,
        s.category_l2 AS category_l2_name,
        c.name AS country,
        g1.geo_l1,
        g2.geo_l2,
        s.gender,
        s.disable_relevant,
        s.income_limit,
        cur.currency_name AS currency,
        s.issuing_body,
        s.is_active,
        s.is_verified,
        s.rating,
        s.creation,
        s.modified
    """

    _JOINS = """
        FROM `tabScheme` s
        LEFT JOIN `tabCountry` c
            ON c.name = s.country
        LEFT JOIN `tabGeography L1` g1
            ON g1.name = s.geo_l1
        LEFT JOIN `tabGeography L2` g2
            ON g2.name = s.geo_l2
        LEFT JOIN `tabCurrency` cur
            ON cur.name = s.currency
    """

    @staticmethod
    def _get_ngos_for_schemes(scheme_ids) -> dict:
        if not scheme_ids:
            return {}

        placeholders = ", ".join(["%s"] * len(scheme_ids))

        query = f"""
            SELECT
                sn.parent AS scheme_id,
                o.name AS ngo_id,
                o.org_name AS ngo_name,
                o.phone
            FROM `tabOrganisation Child Table` sn
            INNER JOIN `tabOrganisation` o
                ON o.name = sn.ngo
            WHERE sn.parent IN ({placeholders})
            ORDER BY sn.parent, sn.idx
        """
        rows = frappe.db.sql(query, scheme_ids, as_dict=True)

        ngos_by_scheme: dict[str, list[NGO]] = {}

        for row in rows:
            ngo = NGO(
                id=row["ngo_id"],
                name=row["ngo_name"],
                phone=row["phone"],
            )
            ngos_by_scheme.setdefault(row["scheme_id"], []).append(ngo)

        return ngos_by_scheme

    @staticmethod
    def get_list(
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
        gender=None,
        disabled=None,
        verified=None,
        lang="en",
        status="Approved",
     
    ) -> Result:
        """Fetch a paginated, filterable list of schemes."""
        try:
            limit = max(SchemeManager.MIN_LIMIT, min(int(limit), SchemeManager.MAX_LIMIT))
            offset = max(0, int(offset))

            where_clause, values = SchemeManager._build_filters(
                category_l1=category_l1,
                category_l2=category_l2,
                country=country,
                geo1=geo1,
                geo2=geo2,
                gender=gender,
                disabled=disabled,
                verified=verified,
                status=status,
            )
            values.extend([limit, offset])

            query = f"""
                SELECT
                    {SchemeManager._SELECT_FIELDS}
                {SchemeManager._JOINS}
                {where_clause}
                ORDER BY s.modified DESC
                LIMIT %s OFFSET %s
            """

            scheme_rows = frappe.db.sql(query, values, as_dict=True)

            scheme_ids = [row["id"] for row in scheme_rows]
            ngos_by_scheme = SchemeManager._get_ngos_for_schemes(scheme_ids)

            scheme_list = []
            for row in scheme_rows:
                scheme = SchemeManager._create_scheme_summary(row,lang=lang)
                scheme_list.append(scheme.model_dump())

            return Result.success(
                message="Schemes fetched successfully.",
                data={
                    "schemes": scheme_list,
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(scheme_list) == limit,
                },
            )

        except Exception as e:
            ErrorLogger.log(e)
            raise

    @staticmethod
    def get(scheme_id: str, lang: str = "en") -> Result:
        """Fetch a single scheme by id."""
        try:
            query = f"""
                SELECT
                    {SchemeManager._SELECT_FIELDS}
                {SchemeManager._JOINS}
                WHERE s.name = %s
                AND s.is_active = 1
            """

            scheme_rows = frappe.db.sql(query, (scheme_id,), as_dict=True)

            if not scheme_rows:
                return Result.not_found("Scheme not found.")

            scheme = SchemeManager._create_scheme(scheme_rows[0], lang=lang)
            ngos = SchemeManager._get_ngos_for_schemes([scheme_id])
            scheme.ngos = ngos.get(scheme_id, [])

            return Result.success(
                message="Scheme fetched successfully.",
                data=scheme.model_dump(),
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
        gender=None,
        disabled=None,
        verified=None,
        status="Approved",
        
    ):
        filters = ["s.is_active = 1"]
        values = []

        # Category filters
        if category_l1:
            filters.append("s.category_l1 = %s")
            values.append(category_l1)
        if category_l2:
            # Exact L2 match
            filters.append("s.category_l2 = %s")
            values.append(category_l2)

        # Location filters
        if country:
            filters.append("c.name = %s")
            values.append(country)

        if geo1:
            filters.append("g1.geo_l1 = %s")
            values.append(geo1)

        if geo2:
            filters.append("g2.geo_l2 = %s")
            values.append(geo2)

        # Other filters
        if gender:
            filters.append("s.gender = %s")
            values.append(gender)

        if disabled is not None:
            filters.append("s.disable_relevant = %s")
            values.append(disabled)

        if verified is not None:
            filters.append("s.is_verified = %s")
            values.append(verified)
        if status is not None:
            filters.append("s.status = %s")
            values.append(status)
      

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        return where_clause, values

    @staticmethod
    def _create_scheme_summary(row: dict, lang: str = "en") -> SchemeSummary:
        return SchemeSummary(
            id=row["id"],
            scheme_name=row["scheme_name"],
            description=row["description"],
            location={
                "country": { "name": row["country"], "display_name": frappe._(row["country"],lang )},
                "geo1": { "name": row["geo_l1"], "display_name": frappe._(row["geo_l1"],lang ) },
                "geo2": { "name": row["geo_l2"], "display_name": frappe._(row["geo_l2"],lang ) }
            },
            disabled_relevant=row["disable_relevant"],
            currency=row["currency"],
            is_active=row["is_active"],
            is_verified=row["is_verified"],
            creation=row["creation"],
            modified=row["modified"],
            gender=row["gender"],
            income_limit=row["income_limit"],
            issuing_body=row["issuing_body"],
            rating=row["rating"],
            scheme_category={
                "l1": { "name": row["category_l1_name"], "display_name": frappe._(row["category_l1_name"],lang ) },
                "l2": { "name": row["category_l2_name"], "display_name": frappe._(row["category_l2_name"],lang ) },
            },
        )

    @staticmethod
    def _create_scheme(row: dict, lang: str = "en") -> Scheme:
        return Scheme(
            id=row["id"],
            scheme_name=row["scheme_name"],
            description=row["description"],
            benefits=row["benefit"],
            eligibility=row["eligibility"],
            documents_required=row["documents_required"],
            application_url=row["application_url"],
            location={
                "country": { "name": row["country"], "display_name": frappe._(row["country"],lang ) },
                "geo1": { "name": row["geo_l1"], "display_name": frappe._(row["geo_l1"],lang ) },
                "geo2": { "name": row["geo_l2"], "display_name": frappe._(row["geo_l2"],lang ) }
            },
            gender=row["gender"],
            disabled_relevant=row["disable_relevant"],
            income_limit=row["income_limit"],
            currency=row["currency"],
            issuing_body=row["issuing_body"],
            is_active=row["is_active"],
            is_verified=row["is_verified"],
            rating=row["rating"],
            creation=row["creation"],
            modified=row["modified"],
            scheme_category={
                "l1": { "name": row["category_l1_name"], "display_name": frappe._(row["category_l1_name"],lang ) },
                "l2": { "name": row["category_l2_name"], "display_name": frappe._(row["category_l2_name"],lang ) },
            },
        )