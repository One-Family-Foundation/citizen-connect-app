import frappe

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.result import Result


class SchemeManager:
    _SELECT_FIELDS = """
        s.name AS id,
        s.scheme_name,
        s.description,
        s.benefit,
        s.eligibility,
        s.documents_required,
        s.application_url,

        l1.catalogue_name AS category_l1_name,
        l2.catalogue_name AS category_l2_name,

        c.name AS country,
        g1.geo_l1,
        g2.geo_2,

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

        LEFT JOIN `tabService Category` l1
            ON l1.name = s.category_l1

        LEFT JOIN `tabService Category` l2
            ON l2.name = s.category_l2

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
    def get_list(
        limit=10,
        offset=0,
        category_l1=None,
        category_l2=None,
        country=None,
        geo1=None,
        geo2=None,
        gender=None,
        disabled=None,
        verified=None,
        active=None,
    ) -> Result:
        try:
            # Validate pagination parameters
            limit = max(1, min(int(limit), 100))
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
                active=active,
            )

            values.extend([limit, offset])

            schemes = frappe.db.sql(
                f"""
                SELECT
                    {SchemeManager._SELECT_FIELDS}
                {SchemeManager._JOINS}
                {where_clause}
                ORDER BY s.modified DESC
                LIMIT %s OFFSET %s
                """,
                values,
                as_dict=True,
            )

            # Transform raw rows into domain objects (summary shape only)
            scheme_list = []
            for row in schemes:
                scheme = SchemeManager._create_scheme_summary(row)
                scheme_list.append(scheme)

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
    def get(scheme_id: str) -> Result:
        try:
            scheme = frappe.db.sql(
                f"""
                SELECT
                    {SchemeManager._SELECT_FIELDS}
                {SchemeManager._JOINS}
                WHERE s.name = %s
                """,
                (scheme_id,),
                as_dict=True,
            )

            if not scheme:
                return Result.not_found(message="Scheme not found.")

            row = scheme[0]
            scheme_data = SchemeManager._create_scheme(row)

            ngos = SchemeManager._get_ngos_for_schemes([scheme_id])
            scheme_data["ngos"] = ngos.get(scheme_id, [])

            return Result.success(
                message="Scheme fetched successfully.",
                data=scheme_data,
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
        active=None,
    ):
        """Builds the WHERE clause + bound values for get_list()'s filters."""
        filters = []
        values = []

        if category_l1:
            filters.append("s.category_l1 = %s")
            values.append(category_l1)
        if category_l2:
            filters.append("s.category_l2 = %s")
            values.append(category_l2)
        if country:
            filters.append("c.name = %s")
            values.append(country)
        if geo1:
            filters.append("g1.geo_l1 = %s")
            values.append(geo1)
        if geo2:
            filters.append("g2.geo_2 = %s")
            values.append(geo2)
        if gender:
            filters.append("s.gender = %s")
            values.append(gender)
        if disabled is not None:
            filters.append("s.disable_relevant = %s")
            values.append(disabled)
        if verified is not None:
            filters.append("s.is_verified = %s")
            values.append(verified)
        if active is not None:
            filters.append("s.is_active = %s")
            values.append(active)

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        return where_clause, values

    @staticmethod
    def _get_ngos_for_schemes(scheme_ids):
        if not scheme_ids:
            return {}

        placeholders = ", ".join(["%s"] * len(scheme_ids))

        rows = frappe.db.sql(
            f"""
            SELECT
                sn.parent AS scheme_id,
                o.name AS ngo_id,
                o.org_name AS ngo_name,
                o.phone

            FROM `tabScheme NGO` sn

            INNER JOIN `tabOrganisation` o
                ON o.name = sn.ngo

            WHERE sn.parent IN ({placeholders})
            ORDER BY sn.parent, sn.idx
            """,
            scheme_ids,
            as_dict=True,
        )

        ngos_by_scheme = {}
        for row in rows:
            ngos_by_scheme.setdefault(row["scheme_id"], []).append({
                "id": row["ngo_id"],
                "name": row["ngo_name"],
                "phone": row["phone"],
            })

        return ngos_by_scheme

    @staticmethod
    def _create_scheme_summary(row: dict) -> dict:
        return {
            "id": row["id"],
            "scheme_name": row["scheme_name"],
            "description": row["description"],
            "location": {
                "country": row["country"],
                "geo1": row["geo_l1"],
                "geo2": row["geo_2"],
            },
            "gender": row["gender"],
            "issuing_body": row["issuing_body"],
            "rating": row["rating"],
            "scheme_category": {
                "l1": {"name": row["category_l1_name"]},
                "l2": {"name": row["category_l2_name"]},
            },
        }

    @staticmethod
    def _create_scheme(row: dict) -> dict:
        return {
            "id": row["id"],
            "scheme_name": row["scheme_name"],
            "description": row["description"],
            "benefits": row["benefit"],
            "eligibility": row["eligibility"],
            "documents_required": row["documents_required"],
            "application_url": row["application_url"],
            "location": {
                "country": row["country"],
                "geo1": row["geo_l1"],
                "geo2": row["geo_2"],
            },
            "gender": row["gender"],
            "disabled_relevant": row["disable_relevant"],
            "income_limit": row["income_limit"],
            "currency": row["currency"],
            "issuing_body": row["issuing_body"],
            "is_active": row["is_active"],
            "is_verified": row["is_verified"],
            "rating": row["rating"],
            "creation": row["creation"],
            "modified": row["modified"],
            "scheme_category": {
                "l1": {"name": row["category_l1_name"]},
                "l2": {"name": row["category_l2_name"]},
            },
        }