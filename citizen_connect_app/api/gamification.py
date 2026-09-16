import frappe

from citizen_connect_app.services.gamification_manager import (
    get_individual_leaderboard,
    get_geography_leaderboard,
)

from citizen_connect_app.utils.error_logger import ErrorLogger
from samaaja.utils.custom_response import custom_response


@frappe.whitelist(allow_guest=True)
def get_individual(
    lang="en",
    limit=10,
    offset=0,
):
    try:
        limit = int(limit)
        offset = int(offset)

        result = get_individual_leaderboard(
            lang=lang,
            limit=limit,
            offset=offset,
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch individual leaderboard.",
            status_code=500,
            error=True,
        )


@frappe.whitelist(allow_guest=True)
def get_geogrophy(
    lang="en",
    limit=10,
    offset=0,
):
    try:
        limit = int(limit)
        offset = int(offset)

        result = get_geography_leaderboard(
            lang=lang,
            limit=limit,
            offset=offset,
        )

        return result.to_custom_response()

    except Exception as e:
        ErrorLogger.log(e)

        return custom_response(
            message="Failed to fetch geography leaderboard.",
            status_code=500,
            error=True,
        )