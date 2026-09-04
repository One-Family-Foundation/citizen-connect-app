import frappe

from pydantic import ValidationError

from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.services.opportunity_application import count_volunteer_actions
from citizen_connect_app.services.case_manager import get_user_case_count 
from citizen_connect_app.utils.commons import create_media_url
from citizen_connect_app.models.gamificaiton import (IndividualLeaderboardItem , GeographyLeaderboardItem )


def get_individual_leaderboard(
    lang: str = "en",
) -> Result:

    try:
        users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
            },
            fields=[
                "name",
                "first_name",
                "user_image",
            ],
            
        )
        
        leaderboard = []
        
        for user in users:
            

            case_actions = get_user_case_count(
                user.name
            ) or 0

            volunteer_result = count_volunteer_actions(
                user.name
            )

            opportunity_actions = (
                volunteer_result.data or 0
            )

            actions = (
                case_actions
                + opportunity_actions
            )


            points = frappe.db.sql(
                """
                SELECT COALESCE(SUM(points), 0)
                FROM `tabEnergy Point Log`
                WHERE user = %s
                """,
                (user.name,),
            )[0][0]

            profile = frappe.db.get_value(
                "User Profile",
                {
                    "user": user.name
                },
                [
                    "name",
                    "user_type",
                    "org_name",
                    
                ],
                as_dict=True,
            )

            designation = None

            if profile:
                if profile.user_type:
                    designation = profile.user_type

            profile_image = (
                create_media_url(user.user_image)
                if  user.user_image
                else None
            )
            
            leaderboard.append({
                "user_id": user.name,
                "user_name": user.first_name,
                "designation": designation,
                "profile_image": profile_image,
                "actions": actions,
                "points": points,
            })

        # Sort by points first, then actions
        leaderboard.sort(
            key=lambda x: (
                x["points"],
                x["actions"],
            ),
            reverse=True,
        )

        # Add rank after sorting
        for rank, item in enumerate(
            leaderboard,
            start=1
        ):
            item["rank"] = rank

        leaderboard_response = [
            IndividualLeaderboardItem.model_validate(
                item,
                context={"lang": lang},
            )
            for item in leaderboard
        ]

        return Result.success(
            message="Individual leaderboard fetched successfully.",
            data=[
                item.model_dump()
                for item in leaderboard_response
            ],
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch individual leaderboard.",
            data={
                "error": str(e)
            },
            error_data={
                "traceback": frappe.get_traceback()
            },
        )
def get_geography_leaderboard(
    lang: str = "en",
) -> Result:

    try:
        users = frappe.db.sql(
            """
            SELECT
                up.user AS user_id,
                up.geo_l1 AS geography_id
            FROM `tabUser Profile` up
            INNER JOIN `tabUser` u
                ON u.name = up.user
            WHERE
                u.enabled = 1
                AND up.geo_l1 IS NOT NULL
            """,
            as_dict=True,
        )

        # Total points per user
        points_data = frappe.db.sql(
            """
            SELECT
                user,
                SUM(points) AS points
            FROM `tabEnergy Point Log`
            GROUP BY user
            """,
            as_dict=True,
        )

        points_map = {
            item.user: item.points or 0
            for item in points_data
        }

        geography_map = {}

        for user in users:

            geography_id = user.geography_id

            if geography_id not in geography_map:
                geography_map[geography_id] = {
                    "geography_id": geography_id,
                    "actions": 0,
                    "points": 0,
                }

            # User actions
            case_actions = get_user_case_count(
                user.user_id
            ) or 0

            volunteer_result = count_volunteer_actions(
                user.user_id
            )

            opportunity_actions = (
                volunteer_result.data or 0
            )

            actions = (
                case_actions
                + opportunity_actions
            )

            # Add user values to geography
            geography_map[geography_id]["actions"] += actions
            geography_map[geography_id]["points"] += (
                points_map.get(user.user_id, 0)
            )

        leaderboard = list(
            geography_map.values()
        )

        # Highest points first
        leaderboard.sort(
            key=lambda x: (
                x["points"],
                x["actions"],
            ),
            reverse=True,
        )

        # Add rank
        for rank, item in enumerate(
            leaderboard,
            start=1,
        ):
            item["rank"] = rank

        # Geography names
        for item in leaderboard:

            item["geography_name"] = frappe.db.get_value(
                "Geography L1",
                item["geography_id"],
                "geo_l1",
            )

        # Validate with Pydantic
        leaderboard_response = [
            GeographyLeaderboardItem.model_validate(
                item,
                context={"lang": lang},
            )
            for item in leaderboard
        ]

        return Result.success(
            message="Geography leaderboard fetched successfully.",
            data=[
                item.model_dump()
                for item in leaderboard_response
            ],
        )

    except Exception as e:

        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to fetch geography leaderboard.",
            data={
                "error": str(e),
            },
            error_data={
                "traceback": frappe.get_traceback(),
            },
        )